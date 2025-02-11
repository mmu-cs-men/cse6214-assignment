"""
Views for handling review submissions by buyers.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404

from core.models.order import Order
from core.models.review import Review
from core.models.shop import Shop
from core.models.user import User
from core.utils.decorators import allowed_roles


@login_required
@allowed_roles(["buyer", "seller"])
def submit_review(request, shop_id):
    """
    Creates a Review for (user + shop) if none exists.
    We also verify that the user has at least one COMPLETED order referencing this shop.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("buyer-orders")

    # Verify the form token
    form_token = request.POST.get('form_token')
    session_token = request.session.get(f'review_token_{shop_id}')
    
    if not form_token or not session_token or form_token != session_token:
        # Silently ignore duplicate/invalid submissions
        return redirect("buyer-orders")
    
    # Clear the token to prevent reuse
    request.session.pop(f'review_token_{shop_id}', None)

    # Convert the Django auth user to your custom user
    current_user = get_object_or_404(User, email=request.user.email)

    shop = get_object_or_404(Shop, id=shop_id)
    # Check if this user has at least one completed order for that shop
    # We'll look for any Order with 'status=completed' that includes an item from this shop
    completed_orders_for_shop = Order.objects.filter(
        user=current_user,
        status="completed",
        order_items__book_listing__shop=shop,  # or book_listings__shop=shop if your relationships differ
    ).distinct()

    if not completed_orders_for_shop.exists():
        messages.error(
            request,
            "You can only review a shop if you have at least one COMPLETED order with that seller.",
        )
        return redirect("buyer-orders")

    rating_str = request.POST.get("rating")
    comment = request.POST.get("comment", "").strip()

    if not rating_str or not comment:
        messages.error(request, "Please provide both rating and comment.")
        return redirect("buyer-orders")

    try:
        rating = int(rating_str)
    except ValueError:
        messages.error(request, "Invalid rating value.")
        return redirect("buyer-orders")

    # If we find any existing review row for this user+shop, block duplicates
    already_rev = Review.objects.filter(shop=shop, user=current_user).exists()
    if already_rev:
        messages.info(request, "You have already reviewed this seller.")
        return redirect("buyer-orders")

    # Otherwise, create a new row for user + shop
    Review.objects.create(
        shop=shop,
        user=current_user,  # Because your Review model has 'user'
        rating=rating,
        comment=comment,
    )
    messages.success(request, f"Review for {shop.name} submitted successfully!")
    return redirect("buyer-orders")
