from django.urls import path

from .views.orders import orders_page, mark_order_ready

urlpatterns = [
    path("orders/", orders_page, name="seller_orders"),
    path("orders/<int:order_id>/ready/", mark_order_ready, name="mark_order_ready"),
]
