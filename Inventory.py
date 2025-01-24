from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Path, Query, Request
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from schemas import SaleSchema, filter_products
from starlette import status
from send_mail import send_email
from datetime import datetime


router = APIRouter(prefix='/trans_mngmnt', tags=['auth'])


@router.post("/productsale/")
def sale(stock: schemas.SaleSchema,
               session: Session=Depends(get_db)):
    product = session.query(models.PIMS).filter(models.PIMS.name == stock.name).first()
    
    threshold = 60
    email = stock.email

    message = f"""Subject: 

Hello,

This is an automated notification to inform you that the stock for {product.name} has dropped below the set threshold.

Remaining Stock: {product.stock} units
Threshold: {threshold} units

Please review the stock levels and take necessary action to restock as needed to avoid running out of inventory.

Thank you.

Best regards,"""
    if product.stock < threshold or product.stock == 0:
        send_email("syedaghazalzehra89@gmail.com",email,f"Low Stock Alert: {product.name}", message)

    if not product:
        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No product found.")
     
    if product.stock == 0:

        product.is_sold= True
        session.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product has been sold.")
    
    if product.stock < stock.stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock")
    
    if product.stock - stock.stock < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="We are sorry stock is not enough.")
    
    product.stock -=stock.stock
    session.commit()
    email = stock.email

    message = f"""
Hello,

We are pleased to inform you that a sale has been successfully processed for the product "{product.name}".

Details of the sale:
Product Name: {product.name}
Quantity Purchased: {stock.stock} units
Price: {product.price * stock.stock} rupees
Sale Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Thank you for choosing our service.

Best regards,
Your Company Name
Sales Team
"""

    send_email("syedaghazalzehra89@gmail.com",email,"Sale Confirmation", message)

    return {"message": f"Thankyou for your purchase you'll recieve a sale confirmation."}

    
@router.post("/search/products/")
async def search_products(
    search_params: dict,  
    session: Session = Depends(get_db)
):

    name = search_params.get('name')
    category = search_params.get('category')

    if not name and not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Provide at least one search parameter"
        )

    query = session.query(models.PIMS)

    if name:
        query = query.filter(models.PIMS.name.ilike(f"%{name}%"))
    
    if category:
        query = query.filter(models.PIMS.category.ilike(f"%{category}%"))

    filtered_products = query.all()

    if not filtered_products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No products found for search parameters"
        )
    
    return filtered_products


@router.post("/filter/products/")
def get_products(
    price: filter_products, 
    session: Session = Depends(get_db)
):

    search_params = {
        "min_price": price.min_price,
        "max_price": price.max_price,
        "min_stock": price.min_stock,
        "max_stock": price.max_stock
    }
    

    query = session.query(models.PIMS)

    if search_params.get("min_price"):
        query = query.filter(models.PIMS.price >= search_params["min_price"])
    if search_params.get("max_price"):
        query = query.filter(models.PIMS.price <= search_params["max_price"])
    if search_params.get("min_stock"):
        query = query.filter(models.PIMS.price >= search_params["min_stock"])
    if search_params.get("max_stock"):
        query = query.filter(models.PIMS.price <= search_params["max_stock"])

    products = query.all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found matching the criteria")
    
    return {"products": products}




