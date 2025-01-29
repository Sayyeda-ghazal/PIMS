from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import jwt, JWTError
import os, models, time
from starlette import status
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from database import get_db
from sqlalchemy.orm import Session
from itsdangerous import URLSafeTimedSerializer

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
    
    payload = {
        "sub": data["sub"],  
        "email": data["email"], 
        "iat": int(time.time()),  
        "exp": datetime.utcnow() + timedelta(hours=1)  
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def user_access(token:str = Depends(outh2_bearer), session: Session=Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
             raise credentials_exception

    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Permission denied to perform this operation on the selected account.") 
    
    user = session.query(models.Users).filter(models.Users.username == username).first()
    if user is None:
        raise credentials_exception
    return user
