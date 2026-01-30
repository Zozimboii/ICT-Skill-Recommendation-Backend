from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str


class LoginResponse(BaseModel):
    status: str
    message: str
    access_token: str
    token_type: str
    user: UserOut


class RegisterResponse(BaseModel):
    status: str
    user_id: int
