from django.urls import path

from seller.views import *
from .views.orders import orders_page, mark_order_ready

urlpatterns = [
    path("book-listings/", book_listings_page, name="seller-book-listings"),
    path("book-listings/add/", add_book_listing, name="seller-add-book"),
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
    path("profile/", profile_page, name="seller-profile"),
    path("update-shop-name/", update_shop_name, name="update-shop-name"),
    path("orders/", orders_page, name="seller-orders"),
    path("orders/<int:order_id>/ready/", mark_order_ready, name="mark-order-ready"),
    path("dashboard/", seller_dashboard, name="seller-dashboard"),
]
