"""
Order details view for the buyer application.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from core.models.order import Order
from core.models.order_item import OrderItem


@login_required
def order_details_page(request, order_id):
    """
    Displays detailed information about a specific order, including its items
    and total price breakdown.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :param order_id: The unique identifier for the order to be displayed.
    :type order_id: int
    :return: Renders the order details template.
    """
    # Ensure the order belongs to the logged-in user, or raise 404
    order = get_object_or_404(Order, id=order_id, user__email=request.user.email)
    items = OrderItem.objects.select_related("book_listing").filter(order=order)

    context = {"order": order, "items": items}
    return render(request, "buyer/order_details.html", context)
