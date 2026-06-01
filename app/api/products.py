from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product with unique SKU validation."""
    service = ProductService(db)
    return service.create_product(data)


@router.get("", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List all products with optional search and pagination."""
    service = ProductService(db)
    return service.list_products(page=page, page_size=page_size, search=search)


@router.get("/stats")
def get_inventory_stats(db: Session = Depends(get_db)):
    """Get inventory statistics including total value and low stock alerts."""
    service = ProductService(db)
    return service.get_inventory_stats()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a product by ID."""
    service = ProductService(db)
    return service.get_product(product_id)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    """Update a product by ID."""
    service = ProductService(db)
    return service.update_product(product_id, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product by ID."""
    service = ProductService(db)
    service.delete_product(product_id)
