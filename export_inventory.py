import csv
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models, schemas
from database import get_db  
from datetime import datetime

router = APIRouter()

@router.get("/export_inventory/")
def export_inventory(session: Session = Depends(get_db)):
    
    inventory_items = session.query(models.PIMS).all()

    file_name = f"inventory_export_{datetime.now().strftime('%Y-%m-%d')}.csv"

    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow([
            "ID", "Name", "Description", "Price", "Stock", "Category", "Image URL", "Created At", "Updated At", "is_sold"
        ])

        for item in inventory_items:
            writer.writerow([
                item.id, item.name, item.description, item.price, item.stock,
                item.category, item.image_url, item.created_at, item.updated_at
            ])
    
    return {"message": f"Inventory data has been exported to {file_name}"}
