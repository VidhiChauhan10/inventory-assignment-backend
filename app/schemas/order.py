from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from app.models.models import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, description="Quantity must be positive")


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    product_name: Optional[str] = None
    product_sku: Optional[str] = None

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    customer_id: int = Field(..., gt=0)
    items: List[OrderItemCreate] = Field(..., min_length=1)

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v):
        if not v:
            raise ValueError("Order must have at least one item")
        return v


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    total_amount: Decimal
    status: OrderStatus
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
    customer_name: Optional[str] = None

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
