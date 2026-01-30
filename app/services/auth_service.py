from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.models import User
from app.schemas.auth import LoginRequest, RegisterRequest

# def login_user(db: Session, data: LoginRequest):
#     user = db.query(User).filter(User.username == data.username).first()

#     if not user or not verify_password(data.password, user.password):
#         raise HTTPException(status_code=401, detail="Invalid username or password")

#     return {
#         "status": "success",
#         "message": "Login successful",
#         "user": {
#             "id": user.id,
#             "username": user.username,
#         },
#     }

# def register_user(db: Session, data: RegisterRequest):
#     existing_user = db.query(User).filter(User.username == data.username).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Username already exists")

#     user = User(
#         username=data.username,
#         password=hash_password(data.password),
#     )
#     db.add(user)
#     db.commit()
#     db.refresh(user)

#     return {
#         "status": "success",
#         "user_id": user.id,
#     }


def register_user(db: Session, data: RegisterRequest):
    # กัน username ซ้ำ
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    # กัน email ซ้ำ
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        username=data.username,
        email=data.email,
        password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"status": "success", "user_id": user.id}


# def login_user(db: Session, data: LoginRequest):
#     user = db.query(User).filter(User.username == data.username).first()

#     if not user or not verify_password(data.password, user.password):
#         raise HTTPException(status_code=401, detail="Invalid username or password")

#     return {
#         "status": "success",
#         "message": "Login successful",
#         "user": {"id": user.id, "username": user.username, "email": user.email},
#     }

from app.core.jwt import create_access_token


def login_user(db: Session, data: LoginRequest):
    user = db.query(User).filter(User.username == data.username).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": str(user.id), "username": user.username})

    return {
        "status": "success",
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    }
