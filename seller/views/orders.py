from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from core.models.order import Order


@login_required
def orders_page(request):
    """Renders a page displaying all orders placed by buyers."""
    all_orders = Order.objects.all().order_by("-placed_at")  # Fetch all orders

    context = {"orders": all_orders}
    return render(request, "seller/orders.html", context)


@login_required
def mark_order_ready(request, order_id):
    """Marks an order as 'Ready for Courier' via AJAX."""
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        order.status = "Ready for Courier"
        order.save()
        return JsonResponse({"success": True, "order_id": order.id, "status": order.status})

    return JsonResponse({"success": False}, status=400)
