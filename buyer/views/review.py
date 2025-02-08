"""
Views for handling review submissions by buyers.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from core.models.order import Order
from core.models.order_item import OrderItem  # Ensure this model exists
from core.models.review import Review
from core.models.user import User


@login_required
def submit_review(request, order_id):
    """
    Handles the submission of a review for a completed order.

    The buyer submits a rating (via the star widget) and a comment.
    The review is saved for the shop associated with the order (retrieved
    from the order items). After successful submission, the order ID is stored
    in the session to prevent additional reviews for that order.

    :param request: Django HttpRequest object.
    :param order_id: The ID of the order being reviewed.
    :return: Redirects to the orders page.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect(reverse("buyer-orders"))

    # Retrieve the order for the current buyer using the buyer's email
    order = get_object_or_404(Order, id=order_id, user__email=request.user.email)

    if order.status.lower() != "completed":
        messages.error(request, "You can only review completed orders.")
        return redirect(reverse("buyer-orders"))

    try:
        rating = int(request.POST.get("rating"))
        comment = request.POST.get("comment", "").strip()

        # Retrieve the shop from the order items (assuming each order has at least one OrderItem)
        order_items = OrderItem.objects.filter(order=order)
        if not order_items.exists():
            messages.error(
                request, "This order has no associated items to determine the shop."
            )
            return redirect(reverse("buyer-orders"))
        shop = order_items.first().book_listing.shop

        # Get a proper User instance using the buyer's email (as done in orders view)
        user_instance = get_object_or_404(User, email=request.user.email)

        # Create the review record in the database
        Review.objects.create(
            shop=shop, user=user_instance, rating=rating, comment=comment
        )

        # Mark this order as reviewed by storing its ID in session.
        reviewed_orders = request.session.get("reviewed_orders", [])
        if order.id not in reviewed_orders:
            reviewed_orders.append(order.id)
        request.session["reviewed_orders"] = reviewed_orders

        messages.success(request, "Review submitted successfully!")
    except Exception as e:
        messages.error(request, "Failed to submit review. Please try again.")

    return redirect(reverse("buyer-orders"))
