from pydantic import BaseModel, EmailStr
from typing import Optional

class Users(BaseModel):

    username : str
    password : str
    email : EmailStr


class signup_user(BaseModel):

    username : str
    password : str
    email : EmailStr


class login_user(BaseModel):

    username : str
    password : str
    email : EmailStr


class pims(BaseModel):
    name : str        
    description : str                  
    price :  int      
    stock : int
    category  : str             
    image_url :  Optional[str] = None
    created_at :  Optional[str] = None
    updated_at : Optional[str] = None
    class config:
        form_attribute = True


class reset_password(BaseModel):
    token: str
    email: EmailStr
    new_password: str


class PasswordResetRequest(BaseModel):
    email: str