from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from core.models.cart import Cart
from core.models.cart_item import CartItem


@login_required
def cart_page(request):
    """
    Displays the buyer's shopping cart and handles updates and deletions.
    **Handles:**
        - Displays the cart.
        - Removes items from the cart.
    **Context Variables:**
        - ``cart_items``: A queryset of the user's cart items.
        - ``total_price``: The total cost of all items in the cart.
    """

    # Get the logged-in user by email
    current_user = request.user

    # Fetch the cart using the user's email
    try:
        cart = Cart.objects.get(user__email=current_user.email)
        cart_items = CartItem.objects.filter(cart=cart).select_related("book_listing")
    except Cart.DoesNotExist:
        cart = None
        cart_items = []

    # Calculate total price
    total_price = sum(item.book_listing.price * item.quantity for item in cart_items)

    if request.method == "POST":
        item_id = request.POST.get("item_id")
        action = request.POST.get("action")

        # Ensure only the logged-in user's cart is affected
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user__email=current_user.email)

        if action == "remove":
            cart_item.delete()

        return redirect("buyer-cart")  # Refresh cart page after update

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
    }
    return render(request, "buyer/cart.html", context)
