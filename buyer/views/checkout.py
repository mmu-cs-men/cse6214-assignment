"""
Checkout view for the buyer application.
"""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from core.models.cart import Cart
from core.models.cart_item import CartItem
from core.models.order import Order
from core.models.order_item import OrderItem
from core.models.user import User


@login_required
def checkout_page(request):
    """
    Renders a checkout page and handles order creation upon form submission.

    This view retrieves the currently logged-in user's cart items, displays them for review,
    and upon POST request, creates an Order and corresponding OrderItems, clears the cart,
    and redirects to the buyer's orders page.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :return: Renders the checkout template on GET or redirects to the orders page on successful checkout.
    :rtype: django.http.HttpResponse
    """
    current_user = request.user

    # Ensure the User instance exists
    platform_user = User.objects.filter(email=current_user.email).first()
    if not platform_user:
        messages.error(request, "User account not found.")
        return redirect("buyer-orders")

    # Attempt to fetch a Cart belonging to this user
    cart = Cart.objects.filter(user=platform_user).first()
    cart_items = (
        CartItem.objects.select_related("book_listing").filter(cart=cart)
        if cart
        else []
    )

    # Calculate subtotal
    subtotal = sum(item.book_listing.price * item.quantity for item in cart_items)

    # Apply tax
    tax_rate = Decimal("0.06")
    tax_amount = (subtotal * tax_rate).quantize(Decimal("0.01"))
    total_price = (subtotal + tax_amount).quantize(Decimal("0.01"))

    if request.method == "POST":
        # Double-check if the cart still has items before processing
        updated_cart_items = CartItem.objects.filter(cart=cart)
        if not updated_cart_items:

            return redirect(reverse("buyer-checkout"))

        # Create a new order
        order = Order.objects.create(
            user=platform_user,
            status="pending",
            total_price=total_price,
        )

        # Move cart items to order items
        for item in updated_cart_items:
            OrderItem.objects.create(
                order=order,
                book_listing=item.book_listing,
                quantity=item.quantity,
                purchase_price=item.book_listing.price,
            )

        # Clear the cart
        updated_cart_items.delete()

        # Redirect to buyer_orders page
        return redirect(reverse("buyer-orders"))

    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "total_price": total_price,
    }
    return render(request, "buyer/checkout.html", context)
