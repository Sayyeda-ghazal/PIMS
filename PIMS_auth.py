from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends, Path, Request
from database import get_db
import models, schemas
from schemas import pims
from starlette import status
from send_mail import send_email
from authentication import user_access
from models import Users

router = APIRouter(prefix='/pims_auth', tags=['auth'])


@router.get("/viewproducts/")
def viewproduct(session: Session=Depends(get_db),current_user: Users = Depends(user_access)):

    product = session.query(models.PIMS).all()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no book found")

    return product

@router.post("/addproducts/")
def addproduct(item: schemas.pims,
               session: Session=Depends(get_db),
               current_user: Users = Depends(user_access)):

    product = session.query(models.PIMS).filter(models.PIMS.name == item.name and
                                                models.PIMS.category == item.category and
                                                models.PIMS.description == item.description).first()
    
    if product:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="This product already exists")
    
    new_product = models.PIMS(name= item.name, 
                              category = item.category, 
                              description = item.description,
                              price = item.price,
                              stock = item.stock
                              )
    
    session.add(new_product)
    session.commit()
    session.refresh(new_product)

    return {f"Product {new_product.name} added successfully"}

@router.put("/updateproducts/{product_id}")
def updateproducts(product_id:int,
                   item: schemas.pims,
                   session: Session=Depends(get_db),
                   current_user: Users = Depends(user_access)
                  ):
    product = session.query(models.PIMS).get(product_id)

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"product with {product_id} not found.")
    
    if item.name:
     product.name = item.name
    if item.category:
     product.category = item.category
    if item.description:
     product.description = item.description
    if item.price:
     product.price = item.price
    if item.stock:
     product.stock = item.stock
    if item.image_url:
     product.image_url = item.image_url

    session.commit()
    session.refresh(product)
    
    return {"message": "product has been added successfully."}

@router.delete("/deleteproducts/{product_id}")
def deleteproducts(product_id:int,
                   session: Session=Depends(get_db),
                   current_user: Users = Depends(user_access)):
   product = session.query(models.PIMS).get(product_id)
   
   if not product:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product not found.")
   
   session.delete(product)
   session.commit()
   session.close()
   return {f"Product {product_id} was deleted."}

