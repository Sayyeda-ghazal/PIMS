from schemas import Users, signup_user, login_user, PasswordResetRequest
import models 
from fastapi import APIRouter, HTTPException, Depends, Path, Request
from database import get_db
from sqlalchemy.orm import Session
from authentication import bcrypt_context, create_access_token, serializer, generate_reset_token, create_reset_link
from starlette import status
from sqlalchemy import and_
from password_reset_mail import send_reset_email



router = APIRouter(prefix='/users_auth', tags=['auth'])


@router.post("/signup")
def signup(user: signup_user,session: Session = Depends(get_db)):

    new_user = models.Users()
    existing_user = session.query(models.Users).filter(and_(
        models.Users.username == new_user.username,
        models.Users.email == new_user.email
    )).first()

    if existing_user:
        raise HTTPException(status_code= 400, detail= f"{existing_user} already exists.")
    
    new_user.username = user.username

    try:
     if not isinstance(user.password, str):
            raise HTTPException(status_code=400, detail="Password must be a string")
     
     hashed_password = bcrypt_context.hash(user.password)

    except TypeError as e:
     raise HTTPException(status_code=400, detail="Invalid password format")
    
    new_user.password = hashed_password
    new_user.email = user.email
    session.add(new_user)
    session.commit()
    return new_user

@router.get("/login")
def login(user:login_user ,session: Session = Depends(get_db)):
   
   db_user = session.query(models.Users).filter(models.Users.username == user.username).first()
   
   if not db_user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
   
   if not bcrypt_context.verify(user.password, db_user.password):
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
   
   access_token = create_access_token(data={"sub": db_user.username})

   return {"access token": access_token,"token_type":"bearer", "username": db_user.username, "email":db_user.email}
   
@router.post("/request-password-reset/")
async def request_password_reset(data: PasswordResetRequest):
    email = data.email

    token = generate_reset_token(email)
    reset_link = create_reset_link(token)

    send_reset_email("syedaghazalzehra89.com", email, reset_link)

    return {"message": "Password reset email sent successfully!"}