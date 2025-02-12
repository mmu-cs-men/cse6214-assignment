"""
Orders view for the buyer application.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
import uuid

from core.models.order import Order
from core.utils.decorators import allowed_roles
from core.models.review import Review
from core.models.shop import Shop
from core.models.user import User


@login_required
@allowed_roles(["buyer", "seller"])
def orders_page(request):
    current_user = get_object_or_404(User, email=request.user.email)
    user_orders = Order.objects.filter(user=current_user).order_by("-placed_at")

    for order in user_orders:
        # Gather distinct shops for that order
        shops_qs = Shop.objects.filter(
            book_listings__order_items__order=order
        ).distinct()

        seller_data = []
        for shop in shops_qs:
            # Only check by (user, shop)
            already_reviewed = Review.objects.filter(
                user=current_user, shop=shop
            ).exists()

            # Generate a token for each unreviewed shop
            if not already_reviewed:
                token = str(uuid.uuid4())
                request.session[f"review_token_{shop.id}"] = token
                review_token = token
            else:
                review_token = None

            seller_data.append(
                {
                    "shop": shop,
                    "already_reviewed": already_reviewed,
                    "review_token": review_token,
                }
            )

        total_sellers = len(seller_data)
        reviewed_count = sum(s["already_reviewed"] for s in seller_data)
        order.all_sellers_reviewed = reviewed_count == total_sellers
        order.seller_info = seller_data

    return render(request, "buyer/orders.html", {"orders": user_orders})
