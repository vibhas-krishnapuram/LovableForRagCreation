from fastapi import FastAPI, APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import Optional, List
from config.security import *
import uuid
import os 
import json 


from langchain_aws import ChatBedrock
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

from schemas.rag_Models import CreateRAGResponse, RagListItem, RAGQueryRequest
from db.crud import *
from db.database import *
from db.models import * 

from utils.File_Class import PrepareFile 
from utils.docExtract import extract_text_from_file

from utils.rag_utilities import get_embeddings, get_rag_collection, chroma_client, collection_cache, get_cached_db, db_cache

async def create_RAG(RAG_name: str = Form(...),
                    Model: str = Form(...),
                    key: str = Form(...),
                    documents: list[UploadFile] = File(...),
                    current_user_id: str = Depends(get_current_user_token)
                    ):
    user_id = current_user_id
    
    session = SessionLocal()
    exists = session.query(User).filter(User.user_id == user_id).first() is not None
    session.close()
    
    if not exists:
        raise HTTPException(status_code=404, detail="User_Id is not found")


    
    rag_id = str(uuid.uuid4())
    
    rag_dir = os.path.join(BASE_DIR, user_id, rag_id)
    os.makedirs(rag_dir, exist_ok=True)

    saved_files = []

    for doc in documents:
        file_path = os.path.join(rag_dir, doc.filename)
        with open(file_path, "wb") as f:
            f.write(await doc.read())
            saved_files.append(file_path)

    # Create collection name
    collections_name = f"{user_id}_{rag_id}"

    # Process and save each file to ChromaDB
    for file in saved_files:
        prep = PrepareFile(file)
        docs = prep.load_documents()
        chunks = prep.doc_splitter(docs)
        chunks = prep.id_chunks(chunks)

        prep.save_to_chromadb(chunks, collection_name=collections_name, persist_directory=CHROMA_DIR) 

    documents_json = json.dumps(saved_files)

    encrypted_key = encrypt_key(key)

    # Save metadata to rag_table
    insert_rag(rag_id, user_id, RAG_name, Model, encrypted_key, documents_json)

    rag_metadata = {
        "user_id": user_id,
        "RAG_name": RAG_name,
        "Model": Model,
        #"key": encrypted_key,
        "documents": saved_files
    }

    with open(os.path.join(rag_dir, "config.json"), "w") as f:
        json.dump(rag_metadata, f, indent=2)

    return {"RAG_id": rag_id, "chromadb": collections_name}



async def query_rag(
    RAG_id: str,
    request: RAGQueryRequest,
    current_user_id: str = Depends(get_current_user_token),
):
    import time
    start_time = time.time()
    
    user_id = current_user_id

    if not user_id_exists(user_id):
        raise HTTPException(status_code=404, detail="User_Id is not found")

    if not rag_exists(RAG_id) or not check_rag_owner(user_id, RAG_id):
        raise HTTPException(status_code=404, detail="RAG not found or does not belong to user")

    rag_info = get_rag_json(RAG_id)
    query_text = request.query
    modelChosen = rag_info["Model"]

    collection_name = f"{user_id}_{RAG_id}"

    # Use cached DB instance
    db = get_cached_db(collection_name)
    retriever = db.as_retriever(search_kwargs={"k": 3})
    
    retrieval_start = time.time()
    docs = retriever.invoke(query_text)
    retrieval_time = time.time() - retrieval_start

    decrypted_key = decrypt_key(rag_info["key"])

    # Select model
    if modelChosen.lower() == "claude":
        model = ChatBedrock(
            model="anthropic.claude-3-sonnet-20240229-v1:0",
            model_kwargs={"temperature": 0.3},
        )
    elif modelChosen.lower() == "openai":
        os.environ["OPENAI_API_KEY"] = decrypted_key
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    else:
        raise HTTPException(status_code=400, detail="Unsupported model type")

    # Create prompt
    prompt = ChatPromptTemplate.from_template("""
You are a helpful AI assistant.
Use the provided context to answer the user's question.

Context:
{context}

Question:
{question}

Answer clearly and rely on the documents provided before using external knowledge.
If the context doesn't contain relevant information, say so.
""")

    # RAG chain
    chain = (
        {
            "context": retriever | (lambda docs: "\n\n".join([d.page_content for d in docs])),
            "question": RunnablePassthrough(),
        }
        | prompt
        | model
        | StrOutputParser()
    )

    llm_start = time.time()
    response = chain.invoke(query_text)
    llm_time = time.time() - llm_start
    
    total_time = time.time() - start_time

    return {
        "response": response,
        "model_used": rag_info["Model"],
        "RAG_name": rag_info["RAG_name"],
        "documents_retrieved": len(docs),
        "performance": {
            "retrieval_time": f"{retrieval_time:.2f}s",
            "llm_time": f"{llm_time:.2f}s",
            "total_time": f"{total_time:.2f}s"
        }
    }


async def file_query_rag(
    RAG_id: str,
    query: str = Form(...),
    file: UploadFile = File(None),
    current_user_id: str = Depends(get_current_user_token),
    ):
    user_id = current_user_id


    if not user_id_exists(user_id):
        raise HTTPException(status_code=404, detail="User_Id is not found")

    if not rag_exists(RAG_id) or not check_rag_owner(user_id, RAG_id):
        raise HTTPException(status_code=404, detail="RAG not found or does not belong to user")

    rag_info = get_rag_json(RAG_id)
    modelChosen = rag_info["Model"]


    collection_name = f"{user_id}_{RAG_id}"

    embeddings = get_embeddings()

    collection = get_rag_collection(collection_name)


    db = get_cached_db(collection_name)
    retriever = db.as_retriever(search_kwargs={"k": 3})


    docs = retriever.invoke(query)


    uploaded_document = None
    if file:
        uploaded_text = await extract_text_from_file(file)
        if uploaded_text and uploaded_text.strip():
            uploaded_document = Document(page_content=uploaded_text)
            docs.append(uploaded_document)

    decrypted_key = decrypt_key(rag_info["key"])

    if modelChosen.lower() == "claude":
        model = ChatBedrock(
            model="anthropic.claude-3-sonnet-20240229-v1:0",
            model_kwargs={"temperature": 0.3},
        )
    elif modelChosen.lower() == "openai":
        os.environ["OPENAI_API_KEY"] = decrypted_key
        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported model type")

    prompt = ChatPromptTemplate.from_template("""
You are a helpful AI assistant.
Use the provided context to answer the user's question.

Context:
{context}

Question:
{question}

If the context doesn't contain relevant information, say so.
""")

    combined_context = "\n\n".join([d.page_content for d in docs])


    chain = prompt | model | StrOutputParser()
    response = chain.invoke({"context": combined_context, "question": query})

    return {
        "response": response,
        "documents_retrieved": len(docs),
        "uploaded_doc_included": bool(uploaded_document),
    }


async def add_documents_to_rag(
            RAG_id: str,
            new_documents: list[UploadFile] = File(...),
            current_user_id = Depends(get_current_user_token)
):
    user_id = current_user_id

    #check token credentials 
    if not user_id_exists(user_id):
        raise HTTPException(status_code=404, detail="User_Id is not found")

    if not rag_exists(RAG_id) or not check_rag_owner(user_id, RAG_id):
        raise HTTPException(status_code=404, detail="RAG not found or does not belong to user")
    
    #load metadata
    rag_info = get_rag_json(RAG_id)

    #save uploaded files to disk
    rag_dir = os.path.join(BASE_DIR, user_id, RAG_id)
    os.makedirs(rag_dir, exist_ok=True)

    #adding new files to list
    new_saved_files = []

    for file in new_documents:
        save_path = os.path.join(rag_dir, file.filename)
        with open(save_path, "wb") as f:
            f.write(await file.read())
        new_saved_files.append(save_path)
    
    #Convert, Chunk, Embed, Save to Chroma
    collection_name = f"{user_id}_{RAG_id}"

    for file_path in new_saved_files:
        prep = PrepareFile(file_path)
        docs = prep.load_documents()
        chunks = prep.doc_splitter(docs)
        chunks = prep.id_chunks(chunks)

        #save id chunks to chroma db
        prep.save_to_chromadb(chunks, collection_name=collection_name, persist_directory=CHROMA_DIR)


    #Update RAG DB with new documents and metadata
    with SessionLocal() as session:
        rag_row = session.query(Rag_Table).filter(Rag_Table.rag_id == RAG_id).first()

        if rag_row.documents:
            existing_docs = json.loads(rag_row.documents)
        else:
            existing_docs = []
        updated_docs = list(set(existing_docs + new_saved_files))

        rag_row.documents = json.dumps(updated_docs)
        session.commit()

    return {
        "message": "Documents added successfully",
        "new_documents": new_saved_files,
        "total_documents": len(updated_docs)
    } 


def get_all_rag(
    current_user_id: str = Depends(get_current_user_token)
    ):
    user_id = current_user_id

    with SessionLocal() as session:
        rags = session.query(Rag_Table).filter(Rag_Table.user_id == user_id).all()
    
    return [
            {"rag_id": r.rag_id, "rag_name": r.rag_name, "model": r.model}
            for r in rags
        ]


def delete_rag(rag_id: str,
                current_user_id: str = Depends(get_current_user_token)
            ):
    user_id = current_user_id

    if not check_rag_owner(user_id, rag_id):
        raise HTTPException(status_code=404, detail="RAG not found or does not belong to user")
    
    db_deleted, files_deleted, chroma_deleted = delete_rag_by_id(user_id, rag_id)

    if not db_deleted and not files_deleted and not chroma_deleted:
        raise HTTPException(status_code=404, detail="RAG not found")

    return 
      