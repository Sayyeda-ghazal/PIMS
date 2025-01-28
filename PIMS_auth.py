from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from database import get_db
import models, schemas
from schemas import pims
from starlette import status
from authentication import user_access
from models import Users
from sqlalchemy import func

router = APIRouter(prefix='/pims_auth', tags=['pims_auth'])


@router.get("/viewproducts/")
def viewproduct(session: Session=Depends(get_db),
                current_user: Users = Depends(user_access)):

    if current_user.role == "admin":
        product = session.query(models.PIMS).order_by(models.PIMS.name).all()
        
    else:
        product = session.query(models.PIMS).filter(models.PIMS.owner_id == current_user.id).order_by(models.PIMS.name).all()
        if not product:
            return {"message": "You have added nothing yet."}
    
    return product

@router.get("/viewproduct/{product_id}")
def viewproduct_byid(product_id : int, 
                session: Session=Depends(get_db),
                current_user: Users = Depends(user_access)):
    
    product = session.query(models.PIMS).filter(models.PIMS.id == product_id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product with id {product_id} doesn't exist") 
    
    if product.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You are not the owner of this item."
        )
    
@router.post("/addproducts/")
def addproduct(item: schemas.pims,
               session: Session=Depends(get_db),
               current_user: Users = Depends(user_access)):

    product = session.query(models.PIMS).filter(
        func.lower(models.PIMS.name) == func.lower(item.name),
        models.PIMS.category == item.category,
        models.PIMS.description == item.description
    ).first()
    
    if product:
        raise HTTPException(status_code=status.HTTP_302_FOUND,
                            detail="This product already exists")
        
    new_product = models.PIMS(
        name= item.name.lower(),  
        category = item.category, 
        description = item.description,
        price = item.price,
        stock = item.stock,
        owner_id = current_user.id
    )

    if new_product.stock < 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Stock should be greater than zero.")
    
    session.add(new_product)
    session.commit()
    session.refresh(new_product)

    return {f"Product {new_product.name} added successfully"}

@router.put("/updateproducts/{product_id}")
def updateproducts(product_id: int,
                   item: schemas.pims,
                   session: Session=Depends(get_db),
                   current_user: Users = Depends(user_access)
                  ):
    product = session.query(models.PIMS).filter(models.PIMS.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"product with {product_id} not found.")
    
    if product.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You are not the owner of this item."
        )
    
    if item.name:
        product.name = item.name.lower()  
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
    
    return {"message": "product has been updated successfully."}

@router.delete("/deleteproducts/{product_id}")
def deleteproducts(product_id:int,
                   session: Session=Depends(get_db),
                   current_user: Users = Depends(user_access)):
   
   product = session.query(models.PIMS).filter(models.PIMS.id == product_id).first()

   if not product:
       raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} doesn't exist"
        )
   
   
   if product and (product.owner_id == current_user.id or current_user.role == "admin"):
       session.delete(product)
       session.commit()
       return {f"Product {product_id} was successfully deleted."}
       
   if product.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You are not the owner of this item."
        )
   
   
   
   

   

