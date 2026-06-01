from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.customer_repository import CustomerRepository
from app.schemas.order import OrderCreate, OrderListResponse
from app.models.models import Order, OrderStatus
import math


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.product_repo = ProductRepository(db)
        self.customer_repo = CustomerRepository(db)

    def create_order(self, data: OrderCreate) -> Order:
        # Validate customer exists
        customer = self.customer_repo.get_by_id(data.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {data.customer_id} not found",
            )

        # Validate all products and stock levels (before any mutations)
        products = {}
        for item in data.items:
            product = self.product_repo.get_by_id(item.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {item.product_id} not found",
                )
            if product.stock_quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Insufficient stock for '{product.name}' (SKU: {product.sku}). "
                        f"Available: {product.stock_quantity}, Requested: {item.quantity}"
                    ),
                )
            products[item.product_id] = product

        try:
            # Create order
            total_amount = Decimal("0")
            order = self.order_repo.create({
                "customer_id": data.customer_id,
                "total_amount": Decimal("0"),
                "status": OrderStatus.PLACED,
            })

            # Create order items and reduce stock atomically
            for item in data.items:
                product = products[item.product_id]
                unit_price = Decimal(str(product.price))
                subtotal = unit_price * item.quantity
                total_amount += subtotal

                self.order_repo.add_item({
                    "order_id": order.id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": unit_price,
                    "subtotal": subtotal,
                })

                # Reduce stock
                self.product_repo.update(product, {
                    "stock_quantity": product.stock_quantity - item.quantity
                })

            # Update total amount
            order.total_amount = total_amount
            self.db.commit()

            # Re-fetch with all relationships
            return self.order_repo.get_by_id(order.id)

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create order: {str(e)}",
            )

    def get_order(self, order_id: int) -> Order:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found",
            )
        return order

    def list_orders(self, page: int = 1, page_size: int = 10, status: Optional[OrderStatus] = None) -> OrderListResponse:
        skip = (page - 1) * page_size
        items, total = self.order_repo.get_all(skip=skip, limit=page_size, status=status)
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        return OrderListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def cancel_order(self, order_id: int) -> Order:
        order = self.get_order(order_id)
        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is already cancelled",
            )
        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel an order with status '{order.status.value}'",
            )
        try:
            # Restore stock for each item
            for item in order.items:
                product = self.product_repo.get_by_id(item.product_id)
                if product:
                    self.product_repo.update(product, {
                        "stock_quantity": product.stock_quantity + item.quantity
                    })
            self.order_repo.update_status(order, OrderStatus.CANCELLED)
            self.db.commit()
            return self.order_repo.get_by_id(order_id)
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cancel order: {str(e)}",
            )

    def count(self) -> int:
        return self.order_repo.count()
