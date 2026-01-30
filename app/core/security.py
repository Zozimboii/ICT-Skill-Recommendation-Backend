from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    # Argon2 parameters (ค่าเริ่มต้นก็ดีอยู่แล้ว แต่ระบุไว้ชัดเจนดีกว่า)
    argon2__memory_cost=65536,  # 64 MB (default)
    argon2__time_cost=3,  # iterations (default)
    argon2__parallelism=4,  # threads (default)
    argon2__type="id",  # argon2id (แนะนำที่สุด)
)


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False
