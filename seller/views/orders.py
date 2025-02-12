from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from core.models.order import Order
from core.models.order_assignment import OrderAssignment
from core.models.shop import Shop
from core.utils.decorators import allowed_roles


@login_required
@allowed_roles(["seller"])
def orders_page(request):
    """Renders a page displaying orders containing books from the current seller's shop."""
    current_user = request.user
    shop = Shop.objects.filter(user__email=current_user.email).first()

    if not shop:
        context = {"orders": [], "assigned_orders": []}
        return render(request, "seller/orders.html", context)

    # Get orders that have items from this seller's shop
    orders_with_my_books = Order.objects.filter(
        order_items__book_listing__shop=shop
    ).distinct().order_by("-placed_at")

    assigned_orders = OrderAssignment.objects.values_list(
        "order_id", flat=True
    )  # Get assigned orders

    context = {"orders": orders_with_my_books, "assigned_orders": assigned_orders}
    return render(request, "seller/orders.html", context)


@login_required
@allowed_roles(["seller"])
def mark_order_ready(request, order_id):
    """Toggles order status between 'Pending' and 'Ready to Ship' unless courier accepted it."""
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)

        # Prevent modification if courier has already accepted
        if OrderAssignment.objects.filter(order=order).exists():
            return redirect("seller-orders")

        # Toggle logic: 'Pending' → 'Ready to Ship', 'Ready to Ship' → 'Pending'
        if order.status == "pending":
            order.status = "ready_to_ship"
        elif order.status == "ready_to_ship":
            order.status = "pending"

        order.save()
        return redirect("seller-orders")

    return redirect("seller-orders")
