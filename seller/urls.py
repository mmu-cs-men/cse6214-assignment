from django.urls import path

from seller.views import *

urlpatterns = [
    path("profile/", profile_page, name="seller-profile"),
    path("update-shop-name/", update_shop_name, name="update-shop-name"),
]
