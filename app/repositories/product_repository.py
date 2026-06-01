from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.models import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_by_sku(self, sku: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.sku == sku).first()

    def get_all(self, skip: int = 0, limit: int = 10, search: Optional[str] = None):
        query = self.db.query(Product)
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%"),
                )
            )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def create(self, product_data: dict) -> Product:
        product = Product(**product_data)
        self.db.add(product)
        self.db.flush()
        self.db.refresh(product)
        return product

    def update(self, product: Product, update_data: dict) -> Product:
        for key, value in update_data.items():
            setattr(product, key, value)
        self.db.flush()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.flush()

    def get_total_inventory_value(self) -> float:
        result = self.db.query(
            func.sum(Product.price * Product.stock_quantity)
        ).scalar()
        return float(result or 0)

    def get_low_stock(self, threshold: int = 10) -> List[Product]:
        return self.db.query(Product).filter(Product.stock_quantity <= threshold).all()

    def count(self) -> int:
        return self.db.query(func.count(Product.id)).scalar()
