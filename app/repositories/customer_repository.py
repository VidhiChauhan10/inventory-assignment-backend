from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.models import Customer


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def get_by_email(self, email: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 10, search: Optional[str] = None):
        query = self.db.query(Customer)
        if search:
            query = query.filter(
                or_(
                    Customer.name.ilike(f"%{search}%"),
                    Customer.email.ilike(f"%{search}%"),
                    Customer.phone.ilike(f"%{search}%"),
                )
            )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def create(self, customer_data: dict) -> Customer:
        customer = Customer(**customer_data)
        self.db.add(customer)
        self.db.flush()
        self.db.refresh(customer)
        return customer

    def update(self, customer: Customer, update_data: dict) -> Customer:
        for key, value in update_data.items():
            setattr(customer, key, value)
        self.db.flush()
        self.db.refresh(customer)
        return customer

    def delete(self, customer: Customer) -> None:
        self.db.delete(customer)
        self.db.flush()

    def count(self) -> int:
        return self.db.query(func.count(Customer.id)).scalar()
