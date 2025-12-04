from fastapi import HTTPException
import bcrypt
import uuid

from db.crud import insert_user, user_exists, find_use_username
from schemas.auth_Models import LoginRequest, CreateUserRequest
from config.security import *


def create_user_id(request: CreateUserRequest):
    if user_exists(request.username):
        raise HTTPException(status_code=400, detail="User already exists")

    readyHash = request.password.encode("utf-8")
    hash_password = bcrypt.hashpw(readyHash, bcrypt.gensalt()).decode("utf-8")

    user_id = str(uuid.uuid4())
    insert_user(user_id, request.username, hash_password)


    return {"Action": "User Created","user_id": user_id}


def login(request: LoginRequest):
    user = find_use_username(request.username)
    if not user:
        raise HTTPException(status_code=400, detail="User is not found")
    
    if not bcrypt.checkpw(request.password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Invalid Username or Password" )
    
    token = create_access_token({"user_id": user.user_id})
    return {"access_token": token, "token_type": "bearer"}