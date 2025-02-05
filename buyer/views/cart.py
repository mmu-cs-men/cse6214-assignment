from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from core.models.cart_item import CartItem


@login_required(login_url="/login/")  # Redirect unauthenticated users to login
def cart_page(request):
    """
    Displays the buyer's shopping cart and handles updates and deletions.

    **Handles:**
        - Displays the cart.
        - Updates quantity of items.
        - Removes items from the cart.

    **Context Variables:**
        - ``cart_items``: A queryset of the user's cart items.
        - ``total_price``: The total cost of all items in the cart.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: Rendered cart page with context data.
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated:
        return redirect("login")  # Redirect unauthenticated users

    cart_items = CartItem.objects.filter(cart__user_id=request.user.id).select_related(
        "book_listing"
    )
    total_price = sum(item.book_listing.price * item.quantity for item in cart_items)

    if request.method == "POST":
        item_id = request.POST.get("item_id")
        action = request.POST.get("action")

        # Ensure only logged-in users can modify their cart
        cart_item = get_object_or_404(
            CartItem, id=item_id, cart__user_id=request.user.id
        )

        if action == "update":
            new_quantity = int(request.POST.get("quantity", 1))
            if new_quantity > 0:
                cart_item.quantity = new_quantity
                cart_item.save()

        elif action == "remove":
            cart_item.delete()

        return redirect("buyer_cart")  # Refresh cart page after update

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
    }
    return render(request, "buyer/cart.html", context)
