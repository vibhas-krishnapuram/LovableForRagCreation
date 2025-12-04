import shutil
from db.models import *
from db.database import *
import os 

BASE_DIR = "rag_data"
CHROMA_DIR = "./chroma_data" 

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




#### RAG HELPERS

def delete_rag_by_id(user_id: str, rag_id: str):
    collection_name = f"{user_id}_{rag_id}"
    rag_dir = os.path.join(BASE_DIR, user_id, rag_id)
    chroma_path = os.path.join(CHROMA_DIR, collection_name)

    # Delete from DB
    with SessionLocal() as session:
        rag_to_delete = session.query(Rag_Table).filter(
            Rag_Table.rag_id == rag_id,
            Rag_Table.user_id == user_id
        ).first()

        if rag_to_delete:
            session.delete(rag_to_delete)
            session.commit()
            db_deleted = True 
        else:
            db_deleted = False

    # Delete from Filesystem
    if os.path.exists(rag_dir):
        shutil.rmtree(rag_dir)

        # debug statement
        print(f"Deleted user RAG data directory: {rag_dir}")
        files_deleted = True 
    else:
        files_deleted = False 
    
    #Delete Chroma Dir
    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)

        #debug statement
        print(f"Deleted Chroma collection directory: {chroma_path}")
        chroma_deleted = True
    else:
        chroma_deleted = False

    return db_deleted, files_deleted, chroma_deleted

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