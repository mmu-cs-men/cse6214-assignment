from django.urls import path
from courier.views.profile import profile_page

urlpatterns = [
    path("profile/", profile_page, name="courier-profile"),
]
