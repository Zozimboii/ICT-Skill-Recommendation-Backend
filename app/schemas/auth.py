# from pydantic import BaseModel, EmailStr


# class LoginRequest(BaseModel):
#     username: str
#     password: str


# class RegisterRequest(BaseModel):
#     username: str
#     email: EmailStr
#     password: str

from pydantic import BaseModel, EmailStr
from sqlalchemy import Enum

class UserOut(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str


class LoginResponse(BaseModel):
    status: str
    message: str
    access_token: str
    token_type: str
    user: UserOut


class RegisterResponse(BaseModel):
    status: str
    user_id: int



class LoginRequest(BaseModel):
    email: EmailStr 
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str 
    last_name: str   

