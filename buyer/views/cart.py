from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from core.models.cart_item import CartItem


@login_required  # Redirect unauthenticated users to login
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

    if not request.user.is_authenticated:
        return redirect("login")  # Redirect unauthenticated users

    # Fetch cart items belonging to the logged-in user
    cart_items = CartItem.objects.filter(cart__user_id=request.user.id).select_related(
        "book_listing"
    )
    total_price = sum(item.book_listing.price * item.quantity for item in cart_items)

    if request.method == "POST":
        item_id = request.POST.get("item_id")
        action = request.POST.get("action")

        # Fetch the specific cart item if it exists
        cart_item = get_object_or_404(
            CartItem, id=item_id, cart__user_id=request.user.id
        )

        if action == "remove":
            cart_item.delete()

        return redirect("buyer-cart")  # Refresh cart page after update

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
    }
    return render(request, "buyer/cart.html", context)
