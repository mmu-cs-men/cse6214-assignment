"""
Order details view for the buyer application.
"""

from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from core.models.order import Order
from core.models.order_item import OrderItem
from core.utils.decorators import allowed_roles
from core.models.review import Review
from core.models.shop import Shop
from core.models.user import User


@login_required
@allowed_roles(["buyer"])
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

    current_user = get_object_or_404(User, email=request.user.email)
    order = get_object_or_404(Order, id=order_id, user=current_user)

    items = OrderItem.objects.filter(order=order)
    
    # Subtotal, tax, etc.
    subtotal = sum(item.purchase_price * item.quantity for item in items)
    tax_rate = Decimal("0.06")
    tax_amount = (subtotal * tax_rate).quantize(Decimal("0.01"))

    # Distinct shops in this order
    shops_qs = Shop.objects.filter(book_listings__order_items__order=order).distinct()

    # Build a list of (shop, review)
    # Where 'review' is whichever row matches (shop=..., user=current_user)
    shops_with_reviews = []
    for shop in shops_qs:
        # might get .first() or all() if multiple reviews exist
        review = (
            Review.objects.filter(user=current_user, shop=shop)
            .order_by("-created_at")
            .first()
        )
        shops_with_reviews.append((shop, review))

    context = {
        "order": order,
        "items": items,
        "shops_with_reviews": shops_with_reviews,
        "rating_range": [1, 2, 3, 4, 5],
        "subtotal": subtotal,
        "tax_amount": tax_amount,
    }
    return render(request, "buyer/order_details.html", context)
