"""
URL patterns for buyer app.
"""

from django.urls import path

from buyer.views import orders_page, checkout_page, order_details_page

urlpatterns = [
    path("orders/", orders_page, name="buyer-orders"),
    path("checkout/", checkout_page, name="buyer-checkout"),
    path("orders/<int:order_id>/", order_details_page, name="buyer-order-details"),
]
