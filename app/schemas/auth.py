# app/schemas/auth.py

from pydantic import BaseModel, EmailStr

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

# app/api/v1/auth.py — ตรวจสอบว่า login endpoint ส่ง role กลับมาด้วย
# ถ้า AuthResponse schema ยังไม่มี user.role ให้แก้ดังนี้:

# schemas/auth.py
from pydantic import BaseModel
from typing import Optional


class UserInfo(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: str          # ← ต้องมี field นี้

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo     # ← ต้องส่ง user object กลับมา


# ใน login endpoint:
# return AuthResponse(
#     access_token=create_access_token({"sub": str(user.id)}),
#     user=UserInfo.model_validate(user),   # ← include role
# )
