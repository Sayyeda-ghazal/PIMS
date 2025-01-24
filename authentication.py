from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import jwt, JWTError
import os, models, secrets
from starlette import status
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from database import get_db
from sqlalchemy.orm import Session
from itsdangerous import URLSafeTimedSerializer


reset_tokens = {}
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")
serializer = URLSafeTimedSerializer(SECRET_KEY)
DEBUG_MODE = os.getenv("DEBUG", "False") == "True"
outh2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

def hash_password(password: str) -> str:
    return bcrypt_context.hash(password)

def create_token(data: dict):
    
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def user_access(token:str = Depends(outh2_bearer), session: Session=Depends(get_db)):
    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid authentication credentials")
        
        user = session.query(models.Users).filter(models.Users.username == username).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User not found")
        return user

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")

def create_reset_link(token: str) -> str:
    base_url = "http://127.0.0.1:8000/reset-password"  
    return f"{base_url}?token={token}"

