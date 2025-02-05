"""
Orders view for the buyer application.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.models.order import Order


@login_required
def orders_page(request):
    """
    Renders a page displaying all orders placed by the currently logged-in user.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :return: Renders the orders template with a list of user orders.
    :rtype: django.http.HttpResponse
    """
    # Filter orders by user email (assuming request.user.email matches the 'email' field in User model).
    current_user = request.user
    user_orders = Order.objects.filter(user__email=current_user.email).order_by(
        "-placed_at"
    )

    context = {"orders": user_orders}
    return render(request, "buyer/orders.html", context)
