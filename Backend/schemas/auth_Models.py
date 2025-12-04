from pydantic import BaseModel


## Pydantic model for login validation
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"



# Pydantic for creating user
class CreateUserRequest(BaseModel):
    username: str
    password: str

class CreateUserResponse(BaseModel):
    Action: str
    user_id: str