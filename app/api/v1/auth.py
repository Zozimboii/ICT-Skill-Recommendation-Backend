from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(tags=["auth"])  # ✅ ไม่ต้องใส่ prefix แล้ว
auth_service = AuthService()
@router.post("/register", response_model=RegisterResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return auth_service.register_user(db, data)

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login_user(db, data)
# @router.post("/login", response_model=LoginResponse)
# def login(data: LoginRequest, db: Session = Depends(get_db)):
#     return login_user(db, data)


# @router.post("/register", response_model=RegisterResponse)
# def register(data: RegisterRequest, db: Session = Depends(get_db)):
#     return register_user(db, data)
