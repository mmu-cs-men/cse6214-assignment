from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import get_object_or_404, render, redirect

from core.models import (
    BookListing,
    Cart,
    CartItem,
    User,
    Review,
)
from core.utils.decorators import allowed_roles


@login_required
@allowed_roles(["buyer", "seller"])
def book_details_page(request, book_id):
    """
    View function to display the book details page. This function manages the display of book
    details, allows users to add the book to their shopping cart, calculates the shop's average
    rating based on user reviews, and prepares data for rendering in the template.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :param book_id: The unique identifier of the book listing.
    :type book_id: int
    :return: Rendered book details page with book, cart, and review context.
    :rtype: django.http.HttpResponse

    """
    current_user = request.user
    authenticated_user = User.objects.get(email=current_user.email)

    book = get_object_or_404(BookListing, id=book_id)
    cart, created = Cart.objects.get_or_create(user=authenticated_user)
    book_in_cart = CartItem.objects.filter(cart=cart, book_listing=book).exists()

    # Get all reviews for the shop selling this book
    shop_reviews = Review.objects.filter(shop=book.shop)

    # Calculate average rating for the shop
    shop_rating_value = shop_reviews.aggregate(Avg("rating"))["rating__avg"]
    if shop_rating_value:
        shop_rating = round(shop_rating_value, 1)
        full_stars = int(shop_rating_value)
        empty_stars = 5 - full_stars
    else:
        shop_rating = 0
        full_stars = 0
        empty_stars = 5

    total_reviews = shop_reviews.count()

    if request.method == "POST":
        # User clicked "Add to Cart"
        #  Check if cart already has items from a different shop
        cart_items = CartItem.objects.filter(cart=cart)
        if cart_items.exists():
            existing_shop = cart_items.first().book_listing.shop
            if existing_shop != book.shop:
                from django.contrib import messages

                messages.error(
                    request, "You can only add books from the same shop to the cart."
                )
                return redirect("buyer-book-details", book_id=book.id)

        if not book_in_cart:
            CartItem.objects.create(cart=cart, book_listing=book)
            return redirect(
                "buyer-book-details", book_id=book.id
            )  # Refresh page after adding

    context = {
        "book": book,
        "book_in_cart": book_in_cart,
        "shop_rating": shop_rating,
        "total_reviews": total_reviews,
        "shop_reviews": shop_reviews,
        # Pass in ranges for iteration in the template:
        "full_stars_list": range(full_stars),
        "empty_stars_list": range(empty_stars),
    }

    return render(request, "buyer/book_details.html", context)
