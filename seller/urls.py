from django.urls import path
from seller.views import *
from .views.orders import orders_page, mark_order_ready

urlpatterns = [
    path("profile/", profile_page, name="seller-profile"),
    path("update-shop-name/", update_shop_name, name="update-shop-name"),
    path("orders/", orders_page, name="seller_orders"),
    path("orders/<int:order_id>/ready/", mark_order_ready, name="mark_order_ready"),
]
