from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.product_service import ProductService
from app.services.customer_service import CustomerService
from app.services.order_service import OrderService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get aggregated dashboard statistics:
    - Total products, customers, orders
    - Total inventory value
    - Low stock alerts
    """
    product_service = ProductService(db)
    customer_service = CustomerService(db)
    order_service = OrderService(db)

    inventory_stats = product_service.get_inventory_stats()

    return {
        "total_products": inventory_stats["total_products"],
        "total_customers": customer_service.count(),
        "total_orders": order_service.count(),
        "total_inventory_value": inventory_stats["total_inventory_value"],
        "low_stock_items": inventory_stats["low_stock_items"],
    }
