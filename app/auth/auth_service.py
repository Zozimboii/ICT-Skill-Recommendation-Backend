# app/services/auth_service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token

from app.models.user import User
from app.auth.auth_schema import LoginRequest, RegisterRequest

class AuthService:

    def register_user(self, db: Session, data: RegisterRequest):
        # 1. ตรวจสอบว่า Email ซ้ำไหม
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")

        # 2. สร้าง User Object
        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            password_hash=hash_password(data.password),
            role="user" # ตั้งค่า default ตาม model
        )
        
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return {"status": "success", "user_id": user.id}
        except Exception as e:
            db.rollback()
            print(f"Registration Error: {e}")
            raise HTTPException(status_code=500, detail="Database error occurred")

    def login_user(self, db: Session, data: LoginRequest):
        # 1. ค้นหา User ด้วย Email
        user = db.query(User).filter(User.email == data.email).first()

        # 2. ตรวจสอบ User และ Password
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is disabled")
        # 3. สร้าง JWT Token
        token = create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        })

        return {
            "status": "success",
            "message": "Login successful",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": user.role,
            },
        }
