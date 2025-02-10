from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
import os
import base64
from core.constants import CONDITION_CHOICES
from core.models.book_listing import BookListing
from core.models.shop import Shop
from core.utils.decorators import allowed_roles
from core.utils.cdn import imagekit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions


def is_valid_image(image):
    """Helper function to validate image file type."""
    if not image:
        return True  # Image is optional

    valid_extensions = [".jpg", ".jpeg", ".png"]
    ext = os.path.splitext(image.name)[1].lower()
    return ext in valid_extensions


@login_required
@allowed_roles(["seller"])
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


@login_required
@allowed_roles(["seller"])
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
                price_val = float(price)
            except ValueError:
                messages.warning(request, "Price must be a valid number.")
            else:
                if price_val < 0:
                    messages.warning(request, "Price cannot be negative.")
                else:
                    try:
                        uploaded_image_url = None
                        uploaded_image_id = None
                        if image:
                            image_data = image.read()
                            base64_image = base64.b64encode(image_data).decode("utf-8")
                            uploaded_img = imagekit.upload_file(
                                file=base64_image,
                                file_name=image.name,
                                options=UploadFileRequestOptions(
                                    use_unique_file_name=True,
                                    is_private_file=False,
                                ),
                            )
                            uploaded_image_url = uploaded_img.url
                            uploaded_image_id = uploaded_img.file_id

                        BookListing.objects.create(
                            shop=shop,
                            title=title,
                            author=author,
                            condition=condition,
                            price=price_val,
                            image_url=uploaded_image_url,  # image is optional
                            image_id=uploaded_image_id,
                        )
                        messages.success(request, "Book listing added successfully!")
                        return redirect("seller-book-listings")
                    except Exception as e:
                        messages.warning(
                            request, f"Failed to add book listing. Error: {str(e)}"
                        )

    # On GET, render the add book listing page.
    context = {
        "CONDITION_CHOICES": CONDITION_CHOICES,
    }
    return render(request, "seller/add_book_listing.html", context)


@login_required
@allowed_roles(["seller"])
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


@login_required
@allowed_roles(["seller"])
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
                price_val = float(price)
            except ValueError:
                messages.error(request, "Price must be a valid number.")
            else:
                if price_val < 0:
                    messages.error(request, "Price cannot be negative.")
                else:
                    try:
                        if image:
                            image_data = image.read()
                            base64_image = base64.b64encode(image_data).decode("utf-8")
                            uploaded_img = imagekit.upload_file(
                                file=base64_image,
                                file_name=image.name,
                                options=UploadFileRequestOptions(
                                    use_unique_file_name=True,
                                    is_private_file=False,
                                ),
                            )

                            # Only delete old image if new upload was successful
                            if listing.image_id:
                                try:
                                    imagekit.delete_file(listing.image_id)
                                except Exception:
                                    # If deletion fails, just log it but continue with update
                                    print(
                                        f"Failed to delete old image {listing.image_id}"
                                    )

                            listing.image_url = uploaded_img.url
                            listing.image_id = uploaded_img.file_id

                        listing.title = title
                        listing.author = author
                        listing.condition = condition
                        listing.price = price_val
                        listing.save()
                        messages.success(request, "Book listing updated successfully!")
                        return redirect("seller-book-listings")
                    except Exception as e:
                        messages.error(
                            request, f"Failed to update book listing. Error: {str(e)}"
                        )

    context = {
        "listing": listing,
        "CONDITION_CHOICES": CONDITION_CHOICES,
    }
    return render(request, "seller/edit_book_listing.html", context)
