from fastapi import FastAPI, HTTPException, File, Form, UploadFile, Body
from pydantic import BaseModel
import json
import uuid
import os
from langchain_aws import BedrockEmbeddings
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from langchain_aws import ChatBedrock
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI


from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from typing import Optional

#tinyDB for inital stage
from tinydb import TinyDB, Query
import bcrypt

from File_Class import PrepareFile 
from docExtract import extract_text_from_file

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = "rag_data"
CHROMA_DIR = "./chroma_data"  


#DB init
users_db = TinyDB("db/users.json")
rag_db = TinyDB("db/rags.json")
User = Query()
Rag = Query()


@app.get("/")
def home():
    return {"Hello": "World"}


class CreateUserRequest(BaseModel):
    username: str
    password: str

class CreateUserResponse(BaseModel):
    user_id: str

@app.post("/create_user", response_model=CreateUserResponse)
def create_user_id(request: CreateUserRequest):

    existing = users_db.search(User.username == request.username)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    readyHash = request.password.encode("utf-8")
    hash_password = bcrypt.hashpw(readyHash, bcrypt.gensalt()).decode("utf-8")

    user_id = str(uuid.uuid4())

    users_db.insert({
        "user_id": user_id,
        "username": request.username,
        "password": hash_password       
    })

    return {"Action": "User Created","user_id": user_id}


class CreateRAGResponse(BaseModel):
    RAG_id: str

@app.post("/{user_id}/create_rag", response_model=CreateRAGResponse)
async def create_RAG(user_id: str,
                    RAG_name: str = Form(...),
                    Model: str = Form(...),
                    key: str = Form(...),
                    documents: list[UploadFile] = File(...)):

    user = users_db.get(User.user_id == user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User_Id is not found")

    rag = rag_db.get(Rag.rag_name == RAG_name)
    if rag is not None and user:
        raise HTTPException(status_code=404, detail="This Name has already been chosen")
    
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

    # Save metadata to rag_db storage 
    rag_db.insert({
    "rag_id": rag_id,
    "user_id": user_id,
    "RAG_name": RAG_name,
    "Model": Model,
    "key": key,
    "documents": saved_files
})

    rag_info = rag_db.get(Rag.rag_id == rag_id)
    with open(os.path.join(rag_dir, "config.json"), "w") as f:
        json.dump(rag_info, f, indent=2)

    return {"RAG_id": rag_id, "chromadb": collections_name}


class RAGQueryRequest(BaseModel):
    query: str


@app.post("/{user_id}/{RAG_id}/query")
async def query_rag(
    user_id: str,
    RAG_id: str,
    query: Optional[str] = Form(None),       # optional form field
    body: Optional[str] = Body(None),       # optional JSON body
    file: UploadFile | None = File(default=None)
):  
    if body and "query" in body:
        query_text = body["query"]
    elif query:
        query_text = query
    else:
        raise HTTPException(status_code=400, detail="No query provided")

    user = users_db.get(User.user_id == user_id)
    
    if user is None:
        raise HTTPException(status_code=404, detail="User_Id is not found")

    rag = rag_db.get(Rag.rag_id == RAG_id)
    #print(rag)
    if rag is None or rag["user_id"] != user_id:
        #print("User gave:", user_id,  "correct id: ",  rag["user_id"])
        raise HTTPException(status_code=404, detail="RAG not found or does not belong to user")


    rag_info = rag

    chromaDB_collection = f"{user_id}_{RAG_id}"
    modelChosen = rag_info["Model"]

    # Load embeddings
    embedding_fn = BedrockEmbeddings(
        model_id="amazon.titan-embed-text-v2:0",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "us-east-2")
    )

    # Connect to Chroma vector store
    db = Chroma(
        collection_name=chromaDB_collection,
        embedding_function=embedding_fn,
        persist_directory=CHROMA_DIR
    )
    retriever = db.as_retriever(search_kwargs={"k": 3})

    # optional uploaded file
    uploaded_document = None
    if file:
        uploaded_text = await extract_text_from_file(file)
        if uploaded_text and uploaded_text.strip():
            uploaded_document = Document(page_content=uploaded_text)

    # Fetch RAG documents
    docs = retriever.invoke(query_text)

    # Add uploaded doc ONLY if provided
    if uploaded_document:
        docs.append(uploaded_document)

    # Select model
    if modelChosen.lower() == "claude":
        model = ChatBedrock(
            model="anthropic.claude-3-sonnet-20240229-v1:0",
            model_kwargs={"temperature": 0.3}
        )
    elif modelChosen.lower() == "openai":
        os.environ["OPENAI_API_KEY"] = rag_info["key"]
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    # Prompt
    prompt = ChatPromptTemplate.from_template("""
You are a helpful AI assistant.
Use the provided context to answer the user's question.

Context:
{context}

Question: {question}

If the context doesn't contain relevant information, say so.
""")

    # Combine context from RAG + optional uploaded file
    combined_context = "\n\n".join([d.page_content for d in docs])

    chain = prompt | model | StrOutputParser()
    response = chain.invoke({"context": combined_context, "question": query_text})

    return {
        "response": response,
       # "documents_retrieved": len(docs),
       # "uploaded_doc_included": bool(uploaded_document)
    }

    
#8536ce4a-dd4a-4b54-89fa-b1ba6361589d