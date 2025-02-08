from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from core.models.order import Order


@login_required
def orders_page(request):
    """Renders a page displaying all orders placed by buyers."""
    all_orders = Order.objects.all().order_by("-placed_at")  # Fetch all orders
    context = {"orders": all_orders}
    return render(request, "seller/orders.html", context)


@login_required
def mark_order_ready(request, order_id):
    """Toggles order status between empty ('-') and 'pending' when the seller marks it."""
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)

        # Correct toggle logic
        if order.status == "pending":
            order.status = ""  # Reset status to empty (shows '-')
        else:
            order.status = "pending"  # Set to 'pending'

        order.save()
        return redirect("seller_orders")  # Redirect back to orders page

    return redirect("seller_orders")  # Fallback redirect
