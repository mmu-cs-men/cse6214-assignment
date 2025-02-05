"""
URL patterns for buyer app.
"""

from django.urls import path

from buyer.views import checkout_page  # from __init__.py

urlpatterns = [
    path("checkout/", checkout_page, name="buyer-checkout"),
    # other buyer paths (orders, etc.) will go here in future branches
]
