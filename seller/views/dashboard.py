from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, DecimalField
from django.shortcuts import render
from core.models.order import Order
from core.models.order_item import OrderItem
from core.models.user import User as CustomUser

@login_required
def seller_dashboard(request):
    """
    Renders the seller dashboard with statistics and recent orders for the logged-in seller.
    """
    # Get the custom user model instance for the logged-in user
    custom_user = CustomUser.objects.get(email=request.user.email)
    
    # Get all order items for the current seller's listings
    seller_order_items = OrderItem.objects.filter(book_listing__shop__user=custom_user)
    
    # Get completed order items for revenue calculation
    completed_order_items = seller_order_items.filter(order__status="completed")
    
    # Calculate total revenue (80% of sales)
    total_revenue = (
        completed_order_items.aggregate(
            revenue=Sum(
                F("quantity") * F("purchase_price") * 0.8,
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )["revenue"]
        or 0
    )

    # Count total orders (distinct orders containing seller's items)
    total_orders = seller_order_items.values('order').distinct().count()
    
    # Count pending orders
    pending_orders = seller_order_items.filter(
        order__status="pending"
    ).values('order').distinct().count()

    # Count total books sold
    books_sold = completed_order_items.aggregate(
        total=Sum('quantity')
    )['total'] or 0

    # Get recent orders containing seller's items
    recent_orders = Order.objects.filter(
        order_items__book_listing__shop__user=custom_user
    ).distinct().order_by("-placed_at")[:5]

    context = {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "pending_orders": pending_orders,
        "books_sold": books_sold,
        "recent_orders": recent_orders,
    }

    return render(request, "seller/dashboard.html", context)
