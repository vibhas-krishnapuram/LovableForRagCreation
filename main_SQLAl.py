from fastapi import FastAPI, HTTPException, File, Form, UploadFile, Depends
from pydantic import BaseModel
import json
import uuid
import os
from langchain_aws import BedrockEmbeddings
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
import bcrypt

from langchain_aws import ChatBedrock
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

from File_Class import PrepareFile 
from docExtract import extract_text_from_file

from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, Text
from sqlalchemy.orm import Mapped, sessionmaker, mapped_column, declarative_base, relationship

from mainDB_test import Rag

import jwt
from datetime import datetime, timedelta, timezone


from rag_utilities import get_embeddings, get_rag_collection, chroma_client, collection_cache, get_cached_db, db_cache

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



## JWT SETUP, MOVE TO ENV FOR PROD AND BEFORE COMMIT
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = HTTPBearer(description="Paste your JWT token prefixed with 'Bearer '")

# JWT Helper Functions 
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    # Use timezone-aware datetime
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded.get("user_id")
    except jwt.ExpiredSignatureError:
        print("Token has expired")  # Debug logging
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")  # Debug logging
        return None


def get_current_user_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    # Extract the token string from the credentials object
    token_string = credentials.credentials
    user_id = verify_token(token_string)
    if not user_id:
        # This exception detail is critical for debugging
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired token. Check server logs for details."
        )
    return user_id


## SQLALCHEMY DB SETUP
Base = declarative_base()
engine = create_engine("sqlite:///RAG_MAKER.db")
SessionLocal = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    # relationships
    rags = relationship("Rag_Table", back_populates="user")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}')>"

def insert_user(user_id: str, username: str, password: str):
    session = SessionLocal()
    user = User(user_id=user_id, username=username, password=password)
    session.add(user)
    session.commit()
    session.refresh(user)   
    session.close()
    return user

def user_exists(username: str):
    session = SessionLocal()
    exists = session.query(User).filter(User.username == username).first() is not None
    session.close()
    return exists

def find_use_username(username: str):
    session = SessionLocal()
    user = session.query(User).filter(User.username == username).first()
    session.close()
    return user

def get_user_data(username: str):
    if user_exists(username):
        user = find_use_username(username)
        return {
        "user_id": user.user_id,
        "username": user.username,
        "password": user.password,
    }
    else:
        return None
def user_id_exists(user_id: str) -> bool:
    session = SessionLocal()
    user = session.query(User).filter(User.user_id == user_id).first() is not None
    session.close()
    return user



class Rag_Table(Base):
    __tablename__ = "rag_table"

    rag_id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    rag_name: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    key: Mapped[str] = mapped_column(String, nullable=False)
    documents: Mapped[str] = mapped_column(Text)


    # RELATIONSHIP 
    user = relationship("User", back_populates="rags")

    def __repr__(self):
        return f"<Rag_Table(rag_id={self.rag_id}, rag_name='{self.rag_name}')>"
    
def insert_rag(rag_id: str, user_id: str, rag_name: str, model: str, key: str, documents):
    session = SessionLocal()
    rag = Rag_Table(rag_id=rag_id, user_id=user_id, rag_name=rag_name, model=model, key=key, documents=documents)
    session.add(rag)
    session.commit()
    session.refresh(rag)
    session.close()
    return rag

def rag_exists(rag_id: str):
    session = SessionLocal()
    rag = session.query(Rag_Table).filter(Rag_Table.rag_id == rag_id).first() is not None
    session.close()
    return rag

def check_rag_owner(cur_user_id, rag_id: str):
    with SessionLocal() as session:
        rag = session.query(Rag_Table).filter(Rag_Table.rag_id == rag_id).first()
        if rag is None:
            return False
        else:
            return rag.user_id == cur_user_id

def get_rag_json(rag_id: str):
    session = SessionLocal()
    if rag_exists(rag_id):
        rag = session.query(Rag_Table).filter(Rag_Table.rag_id == rag_id).first()
        session.close()
        return {
        "user_id": rag.user_id,
        "RAG_name": rag.rag_name,
        "Model": rag.model,
        "key": rag.key,
        "documents": rag.documents
    }

    else:
        return None

Base.metadata.create_all(engine)

@app.get("/")
def home():
    return {"Hello": "World"}

# Pydantic for creating user
class CreateUserRequest(BaseModel):
    username: str
    password: str

class CreateUserResponse(BaseModel):
    Action: str
    user_id: str

@app.post("/create_user", response_model=CreateUserResponse)
def create_user_id(request: CreateUserRequest):
    if user_exists(request.username):
        raise HTTPException(status_code=400, detail="User already exists")

    readyHash = request.password.encode("utf-8")
    hash_password = bcrypt.hashpw(readyHash, bcrypt.gensalt()).decode("utf-8")

    user_id = str(uuid.uuid4())
    insert_user(user_id, request.username, hash_password)


    return {"Action": "User Created","user_id": user_id}


## Pydantic model for login validation
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    user = find_use_username(request.username)
    if not user:
        raise HTTPException(status_code=400, detail="User is not found")
    
    if not bcrypt.checkpw(request.password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Invalid Username or Password" )
    
    token = create_access_token({"user_id": user.user_id})
    return {"access_token": token, "token_type": "bearer"}


# Pydantic for RAG_ID 
class CreateRAGResponse(BaseModel):
    RAG_id: str

@app.post("/rag/create", response_model=CreateRAGResponse)
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
    
    # Save metadata to rag_table
    insert_rag(rag_id, user_id, RAG_name, Model, key, documents_json)

    rag_metadata = {
        "user_id": user_id,
        "RAG_name": RAG_name,
        "Model": Model,
        "key": key,
        "documents": saved_files
    }

    with open(os.path.join(rag_dir, "config.json"), "w") as f:
        json.dump(rag_metadata, f, indent=2)

    return {"RAG_id": rag_id, "chromadb": collections_name}


class RAGQueryRequest(BaseModel):
    query: str

@app.post("/rag/{RAG_id}/query")
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

    # Select model
    if modelChosen.lower() == "claude":
        model = ChatBedrock(
            model="anthropic.claude-3-sonnet-20240229-v1:0",
            model_kwargs={"temperature": 0.3},
        )
    elif modelChosen.lower() == "openai":
        os.environ["OPENAI_API_KEY"] = rag_info["key"]
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

@app.post("/rag/{RAG_id}/file_query")
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

    # Connect to Chroma wrapper using SAME client + collection name
    db = Chroma(
        client=chroma_client,
        collection_name=collection_name,
        embedding_function=embeddings,
    )

    retriever = db.as_retriever(search_kwargs={"k": 3})


    docs = retriever.invoke(query)


    uploaded_document = None
    if file:
        uploaded_text = await extract_text_from_file(file)
        if uploaded_text and uploaded_text.strip():
            uploaded_document = Document(page_content=uploaded_text)
            docs.append(uploaded_document)

   
    if modelChosen.lower() == "claude":
        model = ChatBedrock(
            model="anthropic.claude-3-sonnet-20240229-v1:0",
            model_kwargs={"temperature": 0.3},
        )
    elif modelChosen.lower() == "openai":
        os.environ["OPENAI_API_KEY"] = rag_info["key"]
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

