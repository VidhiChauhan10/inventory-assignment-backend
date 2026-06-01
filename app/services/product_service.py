from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from app.models.models import Product
import math


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)

    def create_product(self, data: ProductCreate) -> Product:
        # Check SKU uniqueness
        existing = self.repo.get_by_sku(data.sku)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with SKU '{data.sku}' already exists",
            )
        product = self.repo.create(data.model_dump())
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_product(self, product_id: int) -> Product:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found",
            )
        return product

    def list_products(self, page: int = 1, page_size: int = 10, search: Optional[str] = None) -> ProductListResponse:
        skip = (page - 1) * page_size
        items, total = self.repo.get_all(skip=skip, limit=page_size, search=search)
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        return ProductListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def update_product(self, product_id: int, data: ProductUpdate) -> Product:
        product = self.get_product(product_id)
        update_data = data.model_dump(exclude_unset=True)
        # Check SKU uniqueness if being updated
        if "sku" in update_data and update_data["sku"] != product.sku:
            existing = self.repo.get_by_sku(update_data["sku"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Product with SKU '{update_data['sku']}' already exists",
                )
        product = self.repo.update(product, update_data)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete_product(self, product_id: int) -> None:
        product = self.get_product(product_id)
        self.repo.delete(product)
        self.db.commit()

    def get_inventory_stats(self):
        total_value = self.repo.get_total_inventory_value()
        low_stock = self.repo.get_low_stock(threshold=10)
        total_products = self.repo.count()
        return {
            "total_products": total_products,
            "total_inventory_value": total_value,
            "low_stock_items": [
                {"id": p.id, "sku": p.sku, "name": p.name, "stock_quantity": p.stock_quantity}
                for p in low_stock
            ],
        }
