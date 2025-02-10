from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
import os

from core.constants import CONDITION_CHOICES
from core.models.book_listing import BookListing
from core.models.shop import Shop
from core.utils.decorators import allowed_roles


def is_valid_image(image):
    """Helper function to validate image file type."""
    if not image:
        return True  # Image is optional
    
    valid_extensions = ['.jpg', '.jpeg', '.png']
    ext = os.path.splitext(image.name)[1].lower()
    return ext in valid_extensions


@allowed_roles(["seller"])
@login_required
def book_listings_page(request):
    """
    Displays all book listings (that are not bought) for the logged-in seller.
    Also avoids duplicating the "No shop found..." message if it was already set.
    """
    current_user = request.user
    shop = Shop.objects.filter(user__email=current_user.email).first()

    if not shop:
        # Check if "No shop found" was already in the messages queue
        existing_msgs = [m.message for m in messages.get_messages(request)]
        if not any("No shop found for this seller" in msg for msg in existing_msgs):
            messages.error(
                request, "No shop found for this seller. Please set up your shop first."
            )
        listings = []
    else:
        listings = BookListing.objects.filter(shop=shop, bought=False)

    context = {
        "listings": listings,
        "CONDITION_CHOICES": CONDITION_CHOICES,
    }
    return render(request, "seller/book_listings.html", context)


@allowed_roles(["seller"])
@login_required
def add_book_listing(request):
    """
    Displays a form for adding a new book listing. On POST, creates a new listing
    and redirects back to the book listings page with a success message.
    """
    current_user = request.user
    shop = Shop.objects.filter(user__email=current_user.email).first()
    if not shop:
        messages.error(
            request, "No shop found for this seller. Please set up your shop first."
        )
        return redirect("seller-book-listings")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "").strip()
        condition = request.POST.get("condition")
        price = request.POST.get("price")
        image = request.FILES.get("image")  # may be None

        if not (title and author and condition and price):
            messages.error(request, "Please fill in all required fields.")
        elif image and not is_valid_image(image):
            messages.warning(request, "Please upload only JPG or PNG image files.")
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
            except Exception:
                messages.error(request, "Failed to add book listing. Please try again.")

    # On GET, render the add book listing page.
    context = {
        "CONDITION_CHOICES": CONDITION_CHOICES,
    }
    return render(request, "seller/add_book_listing.html", context)


@allowed_roles(["seller"])
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


@allowed_roles(["seller"])
@login_required
def edit_book_listing(request, listing_id):
    """
    Displays a form pre-populated with the details of the specified book listing.
    On POST, updates the book listing in the database.
    """
    current_user = request.user
    shop = Shop.objects.filter(user__email=current_user.email).first()
    if not shop:
        messages.error(
            request, "No shop found for this seller. Please set up your shop first."
        )
        return redirect("seller-book-listings")

    listing = get_object_or_404(BookListing, id=listing_id, shop=shop)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "").strip()
        condition = request.POST.get("condition")
        price = request.POST.get("price")
        image = request.FILES.get("image")  # may be None

        if not (title and author and condition and price):
            messages.error(request, "Please fill in all required fields.")
        elif image and not is_valid_image(image):
            messages.warning(request, "Please upload only JPG or PNG image files.")
        else:
            try:
                listing.title = title
                listing.author = author
                listing.condition = condition
                listing.price = price
                if image:
                    listing.image = image  # update image only if a new one is provided
                listing.save()
                messages.success(request, "Book listing updated successfully!")
                return redirect("seller-book-listings")
            except Exception:
                messages.error(
                    request, "Failed to update book listing. Please try again."
                )

    context = {
        "listing": listing,
        "CONDITION_CHOICES": CONDITION_CHOICES,
    }
    return render(request, "seller/edit_book_listing.html", context)
