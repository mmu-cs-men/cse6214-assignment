"""
Checkout view for the buyer application.
"""

import re
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
    updates the book listing to mark it as bought, and redirects to the buyer's orders page.

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
        cart_items = CartItem.objects.select_related("book_listing").filter(cart=cart)
    except Cart.DoesNotExist:
        cart = None
        cart_items = []

    # Calculate subtotal
    subtotal = Decimal("0.00")
    for item in cart_items:
        subtotal += item.book_listing.price * item.quantity

    # We define a simple 6% tax rate to match the bootstrap template
    tax_rate = Decimal("0.06")
    tax_amount = (subtotal * tax_rate).quantize(Decimal("0.01"))
    total_price = (subtotal + tax_amount).quantize(Decimal("0.01"))

    if request.method == "POST":
        # --- Added Address and Payment Details Verification ---

        # Retrieve the address details and payment fields from the POST data
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        postal_code = request.POST.get("postal_code", "").strip()
        country = request.POST.get("country", "").strip()
        card_number = request.POST.get("card_number", "").strip()
        expiry_date = request.POST.get("expiry_date", "").strip()
        cvv = request.POST.get("cvv", "").strip()

        # Prepare a context to re-render the checkout page on validation errors.
        error_context = {
            "cart_items": cart_items,
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "total_price": total_price,
        }

        # Validate Address Details
        if any(char.isdigit() for char in city):
            messages.error(request, "City name should not contain numbers.")
            return render(request, "buyer/checkout.html", error_context)

        if any(char.isdigit() for char in state):
            messages.error(request, "State name should not contain numbers.")
            return render(request, "buyer/checkout.html", error_context)

        if not postal_code.isdigit():
            messages.error(request, "Postal Code must contain only digits.")
            return render(request, "buyer/checkout.html", error_context)

        if any(char.isdigit() for char in country):
            messages.error(request, "Country name should not contain numbers.")
            return render(request, "buyer/checkout.html", error_context)

        # Validate Payment Details
        if not card_number.isdigit() or len(card_number) != 16:
            messages.error(request, "Card number must be 16 digits.")
            return render(request, "buyer/checkout.html", error_context)

        # Check for MM/YY format (with a valid month from 01 to 12)
        if not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", expiry_date):
            messages.error(request, "Expiration date must be in MM/YY format.")
            return render(request, "buyer/checkout.html", error_context)

        if not cvv.isdigit() or len(cvv) not in (3, 4):
            messages.error(request, "CVV must be 3 or 4 digits.")
            return render(request, "buyer/checkout.html", error_context)

        # Double-check if the cart still has items before processing
        updated_cart_items = CartItem.objects.filter(cart=cart)
        if not updated_cart_items:

            return redirect(reverse("buyer-checkout"))

        # Create a new order with the address details included
        order = Order.objects.create(
            user=User.objects.get(email=current_user.email),
            status="pending",
            total_price=total_price,
            address=address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
        )

        ## Move cart items to order items and mark books as bought (for harris ocd)
        for item in updated_cart_items:
            OrderItem.objects.create(
                order=order,
                book_listing=item.book_listing,
                quantity=item.quantity,
                purchase_price=item.book_listing.price,
            )

            # Mark book as bought
            item.book_listing.bought = True
            item.book_listing.save()

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
