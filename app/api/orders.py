from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.services.order_service import OrderService
from app.schemas.order import OrderCreate, OrderResponse, OrderListResponse
from app.models.models import OrderStatus

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order.
    - Validates customer exists
    - Validates all products exist
    - Validates sufficient stock for every item
    - Atomically reduces stock and creates order
    - Rolls back all changes if any validation fails
    """
    service = OrderService(db)
    return service.create_order(data)


@router.get("", response_model=OrderListResponse)
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[OrderStatus] = Query(None),
    db: Session = Depends(get_db),
):
    """List all orders with optional status filter and pagination."""
    service = OrderService(db)
    return service.list_orders(page=page, page_size=page_size, status=status)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get an order by ID including all items and customer info."""
    service = OrderService(db)
    return service.get_order(order_id)


@router.patch("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """
    Cancel an order.
    - Restores stock for all items
    - Cannot cancel SHIPPED or DELIVERED orders
    """
    service = OrderService(db)
    return service.cancel_order(order_id)
