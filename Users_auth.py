from schemas import Users, signup_user, login_user, PasswordResetRequest, NewPassword
import models , schemas
from fastapi import APIRouter, HTTPException, Depends, Path, Request
from database import get_db
from sqlalchemy.orm import Session
from authentication import bcrypt_context, create_token, create_reset_link, user_access
from starlette import status
from sqlalchemy import and_
from send_mail import send_email
from fastapi.responses import PlainTextResponse


router = APIRouter(prefix='/users_auth', tags=['auth'])


@router.post("/signup")
def signup(user: signup_user,session: Session = Depends(get_db)):


    new_user = models.Users()
    existing_user = session.query(models.Users).filter(and_(
        models.Users.username == user.username,
        models.Users.email == user.email
    )).first()

    if existing_user:
        raise HTTPException(status_code=400, detail=f"User with username '{user.username}' or email '{user.email}' already exists.")
    
    new_user.username = user.username
    username = new_user.username

    try:
        if not isinstance(user.password, str):
            raise HTTPException(status_code=400, detail="Password must be a string")
        
        hashed_password = bcrypt_context.hash(user.password)

    except TypeError as e:
        raise HTTPException(status_code=400, detail="Invalid password format")
    
    new_user.password = hashed_password
    new_user.email = user.email
    email = new_user.email
    message = f"""Dear {username},\n\n You have been registered successfully."""

    send_email(email, email,"Registration successfull", message)

    session.add(new_user)
    session.commit()

    return {"message": "User registered successfully", "user": new_user}

@router.get("/login")
def login(user:login_user ,session: Session = Depends(get_db)):
   
   db_user = session.query(models.Users).filter(models.Users.username == user.username).first()
   
   if not db_user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
   
   if not bcrypt_context.verify(user.password, db_user.password):
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
   
   access_token = create_token(data={"sub": db_user.username})

   return {"access token": access_token,"token_type":"bearer", "username": db_user.username, "email":db_user.email}
   
@router.post("/request-password-reset/")
async def request_password_reset(data: PasswordResetRequest, session: Session = Depends(get_db)):

    db_user = session.query(models.Users).filter().first()
    email = data.email
    token = create_token(data={"sub": db_user.username})
    reset_link = create_reset_link(token)

    message = f"""Password reset email: {token}, Please use this token to reset your password."""
    send_email("syedaghazalzehra89.com",email,"Password Reset Request", message)

    return {"message": "password reset mail sent successfully."}

async def reset_password_page(token: str):
    return f"Your Password Reset Token: {token}\nUse this token in Postman to reset your password."

@router.post("/reset_password/")
def reset_password(user: schemas.reset_password, session: Session = Depends(get_db), current_user: Users = Depends(user_access)):
    
    existing_user = session.query(models.Users).filter(models.Users.email == user.email).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found.")

    try:
        if not isinstance(user.new_password, str):
            raise HTTPException(status_code=400, detail="Password must be a string")
        
        hashed_password = bcrypt_context.hash(user.new_password)
    except TypeError as e:
        raise HTTPException(status_code=400, detail="Invalid password format")

    existing_user.password = hashed_password
    session.commit()

    return {"message": "Password reset successfully."}

@router.delete("/deleteusers/{user_id}")
def deleteproducts(user_id:int,
                   session: Session=Depends(get_db)):
   product = session.query(models.Users).get(user_id)
   
   if not product:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product not found.")
   
   session.delete(product)
   session.commit()
   session.close()
   return {f"User {user_id} was deleted."}