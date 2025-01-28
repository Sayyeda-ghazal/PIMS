from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class Roles(str, Enum):
    user = "user"
    admin = "admin"

class Users(BaseModel):

    username : str
    password : str
    email : EmailStr
    role: Roles = "user"


class signup_user(BaseModel):

    username : str
    password : str
    email : EmailStr
    role: str = "user"


class login_user(BaseModel):

    username : Optional[str] = None
    password : str
    email : Optional[EmailStr] = None


class pims(BaseModel):
    name : str        
    description : str                  
    price :  int      
    stock : int
    category  : str             
    image_url :  Optional[str] = None
    created_at :  Optional[str] = None
    updated_at : Optional[str] = None
    is_sold: bool = False
    owner_id : Optional[int] = None
    class Config:
        form_attribute = True


class resetpassword(BaseModel):
    otp: str
    email: EmailStr
    new_password: str


class PasswordResetRequest(BaseModel):
    email: str

class NewPassword(BaseModel):
    new_password: str

class SaleSchema(BaseModel):
    name: str
    stock: int
    email : EmailStr

class filter_products(BaseModel):
    min_price: Optional[float]
    max_price: Optional[float]
    min_stock: Optional[int] 
    max_stock: Optional[int] 



class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerification(BaseModel):
    email: EmailStr
    otp: str




