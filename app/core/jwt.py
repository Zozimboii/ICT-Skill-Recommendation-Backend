# from datetime import datetime, timedelta
# import os

# import jwt

# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = "HS256"


# def create_access_token(data: dict, expires_minutes: int = 60):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

from fastapi import HTTPException
from datetime import datetime, timedelta
import os
import jwt

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_minutes: int = 60):
    to_encode = data.copy()
    print("SECRET_KEY:", SECRET_KEY)
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expires_minutes)

    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": "access"
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")