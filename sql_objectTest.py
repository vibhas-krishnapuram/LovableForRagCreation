from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Mapped, sessionmaker, mapped_column, declarative_base

Base = declarative_base()
engine = create_engine("sqlite:///test_object.db")
SessionLocal = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}')>"

Base.metadata.create_all(engine)

def insert_user(username: str, password: str):
    session = SessionLocal()
    user = User(username=username, password=password)
    session.add(user)
    session.commit()
    session.refresh(user)   # loads generated ID
    session.close()
    return user

def find_use_username(username: str):
    session = SessionLocal()
    user = session.query(User).filter(User.username == username).first()
    session.close
    return user

def user_exists(username: str):
    session = SessionLocal()
    exists = session.query(User).filter(User.username == username).first() is not None
    session.close()
    return exists

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

insert_user("vibhask09", "password")
insert_user("asdf", "password")
insert_user("asdfasdf", "password")

print(user_exists("vibhask09"))
print(user_exists("vibhask010"))

print(get_user_data("vibhask09"))




# @app.post("/{user_id}/create_rag", response_model=CreateRAGResponse)
# async def create_RAG(user_id: str,
#                     RAG_name: str = Form(...),
#                     Model: str = Form(...),
#                     key: str = Form(...),
#                     documents: list[UploadFile] = File(...)):

#     if user_id not in users_db:
#         raise HTTPException(status_code=404, detail="User_Id is not found")
    

    
#     rag_id = str(uuid.uuid4())
    
#     rag_dir = os.path.join(BASE_DIR, user_id, rag_id)
#     os.makedirs(rag_dir, exist_ok=True)

#     saved_files = []

#     for doc in documents:
#         file_path = os.path.join(rag_dir, doc.filename)
#         with open(file_path, "wb") as f:
#             f.write(await doc.read())
#             saved_files.append(file_path)

#     # Create collection name
#     collections_name = f"{user_id}_{rag_id}"

#     # Process and save each file to ChromaDB
#     for file in saved_files:
#         prep = PrepareFile(file)
#         docs = prep.load_documents()
#         chunks = prep.doc_splitter(docs)
#         chunks = prep.id_chunks(chunks)

#         prep.save_to_chromadb(chunks, collection_name=collections_name, persist_directory=CHROMA_DIR) 

#     # Save metadata to rag_db storage dict
#     rag_db[rag_id] = {
#         "user_id": user_id,
#         "RAG_name": RAG_name,
#         "Model": Model,
#         "key": key,
#         "documents": saved_files
#     }

#     with open(os.path.join(rag_dir, "config.json"), "w") as f:
#         json.dump(rag_db[rag_id], f, indent=2)

#     return {"RAG_id": rag_id, "chromadb": collections_name}
