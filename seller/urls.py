from django.urls import path

from seller.views import dashboard
from seller.views.book_listings import (
    book_listings_page,
    delete_book_listing,
    edit_book_listing,
)

urlpatterns = [
    path("dashboard/", dashboard, name="seller-dashboard"),
    path("book-listings/", book_listings_page, name="seller-book-listings"),
    path(
        "book-listings/delete/<int:listing_id>/",
        delete_book_listing,
        name="seller-delete-book",
    ),
    path(
        "book-listings/edit/<int:listing_id>/",
        edit_book_listing,
        name="seller-edit-book",
    ),
]
