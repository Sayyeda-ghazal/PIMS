from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

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
    is_sold: bool
    class Config:
        form_attribute = True


class reset_password(BaseModel):
    token: str
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

class StockStatusEnum(Enum):
    available = "Available"
    sold = "Sold"



