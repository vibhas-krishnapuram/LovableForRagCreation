from fastapi import APIRouter
from schemas.auth_Models import LoginRequest, LoginResponse, CreateUserRequest, CreateUserResponse
from config.security import *

from auth.service import *


router = APIRouter()

@router.post("/create_user", response_model=CreateUserResponse)
def create_user_id_route(request: CreateUserRequest):
    return_val = create_user_id(request)
    return return_val

@router.post("/login", response_model=LoginResponse)
def login_route(request: LoginRequest):
    return_val = login(request)
    return return_val

