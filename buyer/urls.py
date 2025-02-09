"""
URL patterns for buyer app.
"""

from django.urls import path

from buyer.views import book_details_page
from buyer.views import cart_page
from buyer.views import landing_page
from buyer.views import orders_page, checkout_page, order_details_page
from buyer.views import profile_page
from buyer.views.review import submit_review

urlpatterns = [
    path("orders/", orders_page, name="buyer-orders"),
    path("checkout/", checkout_page, name="buyer-checkout"),
    path("cart/", cart_page, name="buyer-cart"),
    path("landing/", landing_page, name="buyer-landing"),
    path("orders/<int:order_id>/", order_details_page, name="buyer-order-details"),
    path("book/<int:book_id>/", book_details_page, name="buyer-book-details"),
    path("profile/", profile_page, name="buyer-profile"),
    path("review/<int:shop_id>/", submit_review, name="buyer-review"),
]
