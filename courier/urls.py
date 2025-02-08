from django.urls import path

from .views import deliveries_page, accept_order, update_assignment, report_issue

urlpatterns = [
    path("", deliveries_page, name="courier-deliveries"),
    path("accept/<int:order_id>/", accept_order, name="courier-accept-order"),
    path(
        "update/<int:assignment_id>/",
        update_assignment,
        name="courier-update-assignment",
    ),
    path("report/<int:assignment_id>/", report_issue, name="courier-report-issue"),
]
