"""
URL patterns for buyer app.
"""

from django.urls import path

from buyer.views import orders_page

urlpatterns = [
    path("orders/", orders_page, name="buyer-orders"),
]
