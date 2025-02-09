from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from core.models.order import Order
from core.models.order_item import (
    OrderItem,
)  # Assuming this model tracks books in orders


@login_required
def seller_dashboard(request):
    """
    Renders the seller dashboard with statistics and recent orders.
    """
    total_orders = Order.objects.count()
    total_revenue = (
        Order.objects.filter(status="completed").aggregate(Sum("total_price"))[
            "total_price__sum"
        ]
        or 0
    )
    pending_orders = Order.objects.filter(status="pending").count()

    # Count total books sold (sum of all order items from completed orders)
    books_sold = (
        OrderItem.objects.filter(order__status="completed").aggregate(Sum("quantity"))[
            "quantity__sum"
        ]
        or 0
    )

    recent_orders = Order.objects.order_by("-placed_at")[:5]

    context = {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "pending_orders": pending_orders,
        "books_sold": books_sold,
        "recent_orders": recent_orders,
    }

    return render(request, "seller/dashboard.html", context)
