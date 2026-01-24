from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, LoginResponse, RegisterResponse
from app.services.auth_service import login_user, register_user

router = APIRouter(tags=["auth"])  # ✅ ไม่ต้องใส่ prefix แล้ว

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return login_user(db, data)

@router.post("/register", response_model=RegisterResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(db, data)
