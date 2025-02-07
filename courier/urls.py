from django.urls import path

from .views import deliveries_page, update_delivery, report_issue

urlpatterns = [
    path("", deliveries_page, name="courier-index"),  # default landing page
    path("deliveries/", deliveries_page, name="courier-deliveries"),
    path(
        "deliveries/update/<int:assignment_id>/",
        update_delivery,
        name="courier-update-delivery",
    ),
    path(
        "deliveries/report/<int:assignment_id>/",
        report_issue,
        name="courier-report-issue",
    ),
]
