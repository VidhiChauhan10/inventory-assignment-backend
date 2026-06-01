from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.models import Order, OrderItem, OrderStatus


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, order_id: int) -> Optional[Order]:
        return (
            self.db.query(Order)
            .options(
                joinedload(Order.items).joinedload(OrderItem.product),
                joinedload(Order.customer),
            )
            .filter(Order.id == order_id)
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 10, status: Optional[OrderStatus] = None):
        query = self.db.query(Order).options(
            joinedload(Order.items).joinedload(OrderItem.product),
            joinedload(Order.customer),
        )
        if status:
            query = query.filter(Order.status == status)
        query = query.order_by(Order.created_at.desc())
        total = self.db.query(func.count(Order.id))
        if status:
            total = total.filter(Order.status == status)
        total = total.scalar()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def create(self, order_data: dict) -> Order:
        order = Order(**order_data)
        self.db.add(order)
        self.db.flush()
        return order

    def add_item(self, item_data: dict) -> OrderItem:
        item = OrderItem(**item_data)
        self.db.add(item)
        self.db.flush()
        return item

    def update_status(self, order: Order, status: OrderStatus) -> Order:
        order.status = status
        self.db.flush()
        self.db.refresh(order)
        return order

    def count(self) -> int:
        return self.db.query(func.count(Order.id)).scalar()
