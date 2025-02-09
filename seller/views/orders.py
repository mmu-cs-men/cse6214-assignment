from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from core.models.order import Order
from core.models.order_assignment import OrderAssignment
from core.utils.decorators import allowed_roles


@login_required
@allowed_roles(["seller"])
def orders_page(request):
    """Renders a page displaying all orders placed by buyers."""
    all_orders = Order.objects.all().order_by("-placed_at")  # Fetch all orders
    assigned_orders = OrderAssignment.objects.values_list(
        "order_id", flat=True
    )  # Get assigned orders

    context = {"orders": all_orders, "assigned_orders": assigned_orders}
    return render(request, "seller/orders.html", context)


@login_required
@allowed_roles(["seller"])
def mark_order_ready(request, order_id):
    """Toggles order status between 'Pending' and 'Ready to Ship' unless courier accepted it."""
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)

        # Prevent modification if courier has already accepted
        if OrderAssignment.objects.filter(order=order).exists():
            return redirect("seller_orders")

        # Toggle logic: 'Pending' → 'Ready to Ship', 'Ready to Ship' → 'Pending'
        if order.status == "pending":
            order.status = "ready_to_ship"
        elif order.status == "ready_to_ship":
            order.status = "pending"

        order.save()
        return redirect("seller_orders")

    return redirect("seller_orders")
