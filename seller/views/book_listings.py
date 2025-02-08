from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from core.constants import CONDITION_CHOICES
from core.models.book_listing import BookListing
from core.models.shop import Shop


@login_required
def book_listings_page(request):
    """
    Displays all book listings for the logged-in seller.
    Also handles the addition of a new book listing.
    """
    # Get the seller's shop (assuming one shop per seller)
    current_user = request.user
    shop = Shop.objects.filter(user__email=current_user.email).first()
    if not shop:
        messages.error(
            request, "No shop found for this seller. Please set up your shop first."
        )
        listings = []
    else:
        # Only retrieve listings that have not been bought.
        listings = BookListing.objects.filter(shop=shop, bought=False)

    # If the request is POST, handle new book listing creation.
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "").strip()
        condition = request.POST.get("condition")
        price = request.POST.get("price")
        image = request.FILES.get("image")  # may be None

        # Simple validation:
        if not (title and author and condition and price):
            messages.error(request, "Please fill in all required fields.")
        else:
            try:
                BookListing.objects.create(
                    shop=shop,
                    title=title,
                    author=author,
                    condition=condition,
                    price=price,
                    image=image,  # image is optional
                )
                messages.success(request, "Book listing added successfully!")
                return redirect("seller-book-listings")
            except Exception as e:
                messages.error(request, "Failed to add book listing. Please try again.")

    context = {
        "listings": listings,
        "CONDITION_CHOICES": CONDITION_CHOICES,
    }
    return render(request, "seller/book_listings.html", context)


@login_required
def delete_book_listing(request, listing_id):
    """
    Deletes a book listing for the seller after confirmation.
    """
    current_user = request.user
    shop = Shop.objects.filter(user__email=current_user.email).first()
    listing = get_object_or_404(BookListing, id=listing_id, shop=shop)
    if request.method == "POST":
        listing.delete()
        messages.success(request, "Book listing deleted successfully!")
    else:
        messages.error(request, "Invalid request.")
    return redirect("seller-book-listings")


def edit_book_listing(request, listing_id):
    """
    Placeholder view for editing a book listing.
    Redirects back to the Seller Book Listings page with a query parameter.
    """
    url = f"{reverse('seller-book-listings')}?edit=1"
    return redirect(url)
