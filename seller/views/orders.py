from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from core.models.order import Order
from core.models.order_assignment import OrderAssignment  # Import assignment model


@login_required
def orders_page(request):
    """Renders a page displaying all orders placed by buyers."""
    all_orders = Order.objects.all().order_by("-placed_at")  # Fetch all orders

    # Fetch assigned orders (orders already taken by a courier)
    assigned_orders = set(OrderAssignment.objects.values_list("order_id", flat=True))

    context = {
        "orders": all_orders,
        "assigned_orders": assigned_orders,  # Pass assigned order IDs to template
    }
    return render(request, "seller/orders.html", context)


@login_required
def mark_order_ready(request, order_id):
    """Toggles order status between 'pending' and 'ready_to_ship', but prevents unmarking if assigned."""
    order = get_object_or_404(Order, id=order_id)

    # Check if the order has been assigned to a courier
    if OrderAssignment.objects.filter(order=order).exists():
        return redirect("seller_orders")  # Prevent status toggle if assigned

    if request.method == "POST":
        # Toggle logic: 'Pending' → 'Ready to Ship', 'Ready to Ship' → 'Pending'
        if order.status == "pending":
            order.status = "ready_to_ship"
        elif order.status == "ready_to_ship":
            order.status = "pending"

        order.save()
        return redirect("seller_orders")  # Redirect back to orders page

    return redirect("seller_orders")  # Fallback redirect
