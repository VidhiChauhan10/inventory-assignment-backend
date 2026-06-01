from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerListResponse
from app.models.models import Customer
import math


class CustomerService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CustomerRepository(db)

    def create_customer(self, data: CustomerCreate) -> Customer:
        existing = self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Customer with email '{data.email}' already exists",
            )
        customer = self.repo.create(data.model_dump())
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def get_customer(self, customer_id: int) -> Customer:
        customer = self.repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found",
            )
        return customer

    def list_customers(self, page: int = 1, page_size: int = 10, search: Optional[str] = None) -> CustomerListResponse:
        skip = (page - 1) * page_size
        items, total = self.repo.get_all(skip=skip, limit=page_size, search=search)
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        return CustomerListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def update_customer(self, customer_id: int, data: CustomerUpdate) -> Customer:
        customer = self.get_customer(customer_id)
        update_data = data.model_dump(exclude_unset=True)
        if "email" in update_data and update_data["email"] != customer.email:
            existing = self.repo.get_by_email(update_data["email"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Customer with email '{update_data['email']}' already exists",
                )
        customer = self.repo.update(customer, update_data)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def delete_customer(self, customer_id: int) -> None:
        customer = self.get_customer(customer_id)
        self.repo.delete(customer)
        self.db.commit()

    def count(self) -> int:
        return self.repo.count()
