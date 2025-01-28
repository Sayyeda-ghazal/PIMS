from schemas import Users, signup_user, login_user, PasswordResetRequest
import models , schemas
from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from sqlalchemy.orm import Session
from authentication import bcrypt_context, create_token, create_reset_link, user_access
from starlette import status
from sqlalchemy import or_
from send_mail import send_email



router = APIRouter(prefix='/users_auth', tags=['users_auth'])


@router.post("/signup")
def signup(user: signup_user, session: Session = Depends(get_db)):

    existing_user_by_username = session.query(models.Users).filter(models.Users.username == user.username).first()
    existing_user_by_email = session.query(models.Users).filter(models.Users.email == user.email).first()

    if existing_user_by_username:
        raise HTTPException(status_code=400, detail=f"Username '{user.username}' already exists.")
    if existing_user_by_email:
        raise HTTPException(status_code=400, detail=f"Email '{user.email}' already exists.")
    
    new_user = models.Users()
    new_user.username = user.username
    username = new_user.username

    if not any(char.isalpha() for char in user.username):
        raise HTTPException(
            status_code=400,
            detail="Username must contain at least one alphabet."
        )
    
    if user.username[0].isdigit():
        raise HTTPException(
            status_code=400,
            detail="Username must not start with a number."
        )

    if not isinstance(user.password, str):
        raise HTTPException(status_code=400, detail="Password must be a string")
    
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

    try:
        hashed_password = bcrypt_context.hash(user.password)
    except TypeError:
        raise HTTPException(status_code=400, detail="Invalid password format")

    new_user.password = hashed_password
    new_user.email = user.email
    new_user.role = user.role if user.role in ["admin", "user"] else "user"  # Assign role
    email = new_user.email

    message = f"""Dear {username},\n\nYou have been registered successfully."""
    send_email(email, email, "Registration Successful", message)

    session.add(new_user)
    session.commit()

    return {"message": "User registered successfully", "user": {"username": username, "email": email,  "role": new_user.role}}


@router.get("/login")
def login(user: login_user, session: Session = Depends(get_db)):

    db_user = session.query(models.Users).filter(
        or_(
            models.Users.username == user.username,
            models.Users.email == user.username
        )
    ).first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid username/email or password.")

    if not bcrypt_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_token(data={"sub": db_user.username, "email": db_user.email})

    return {
        "access token": access_token,
        "token_type": "bearer",
        "username": db_user.username,
        "email": db_user.email,
        "role": db_user.role
    }

@router.post("/request-password-reset/")
async def request_password_reset(data: PasswordResetRequest,
                                session: Session = Depends(get_db),
                                current_user: Users = Depends(user_access)):
    

    if current_user.role != "admin" and current_user.email != data.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to reset another user's password.")


    db_user = session.query(models.Users).filter(models.Users.email == data.email).first()
    
    email = data.email
    token = create_token(data={"sub": db_user.username, "email":db_user.email})

    message = f"""Password reset email: {token}, Please use this token to reset your password."""
    send_email("syedaghazalzehra89.com",email,"Password Reset Request", message)

    return {"message": "password reset mail sent successfully."}

async def reset_password_page(token: str):
    return f"Your Password Reset Token: {token}\nUse this token in Postman to reset your password."

@router.post("/reset_password/")
def reset_password(user: schemas.reset_password,
                   data: PasswordResetRequest,
                   session: Session = Depends(get_db), 
                   current_user: Users = Depends(user_access)):
    
    if current_user.role != "admin" and current_user.email != data.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to reset another user's password.")
    
    existing_user = session.query(models.Users).filter(models.Users.email == user.email).first()

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
def deleteuser(user_id:int,
               session: Session=Depends(get_db), 
               current_user: Users = Depends(user_access)):
   user = session.query(models.Users).get(user_id)
   
   if not user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"User doesn't exists.")
   
   if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to reset another user's password.")
   
   if current_user.email != current_user.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are successfully removed..")
   
   session.delete(user)
   session.commit()
   session.close()
   return {f"User {user_id} was deleted."}



