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
    # Get the logged-in user (Django's auth user is our 'User' or you might be bridging them)
    current_user = request.user

    # Attempt to fetch a Cart belonging to this user; if none, context remains empty
    try:
        cart = Cart.objects.get(user__email=current_user.email)
    except Cart.DoesNotExist:
        cart = None

    cart_items = (
        CartItem.objects.select_related("book_listing").filter(cart=cart)
        if cart
        else []
    )

    # Calculate subtotal
    subtotal = Decimal("0.00")
    for item in cart_items:
        subtotal += item.book_listing.price * item.quantity

    # We define a simple 6% tax rate to match the bootstrap template
    tax_rate = Decimal("0.06")
    tax_amount = (subtotal * tax_rate).quantize(Decimal("0.01"))
    total_price = (subtotal + tax_amount).quantize(Decimal("0.01"))

    if request.method == "POST":
        # Double-check if the cart actually has items now
        updated_cart_items = CartItem.objects.filter(cart=cart)
        if not updated_cart_items:
            messages.warning(
                request, "Your cart was already emptied. Nothing to checkout."
            )
            return redirect(reverse("buyer-checkout"))

        # Create a new order
        order = Order.objects.create(
            user=User.objects.get(email=current_user.email),
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

        # Redirect to the orders page
        return redirect(reverse("buyer-orders"))

    # Render the checkout page on GET
    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "total_price": total_price,
    }
    return render(request, "buyer/checkout.html", context)
