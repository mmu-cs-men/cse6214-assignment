"""
Views for managing courier deliveries.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from core.models.delivery_issue import DeliveryIssue
from core.models.order_assignment import OrderAssignment


@login_required
def deliveries_page(request):
    """
    Renders a page listing all order assignments for delivery.

    :param request: Django HttpRequest object.
    :return: Rendered deliveries page with assignments.
    """
    assignments = OrderAssignment.objects.all().order_by("-updated_at")
    context = {
        "assignments": assignments,
    }
    return render(request, "courier/deliveries.html", context)


@login_required
def update_delivery(request, assignment_id):
    """
    Handles POST requests to update an OrderAssignment's status.

    :param request: Django HttpRequest object.
    :param assignment_id: The ID of the OrderAssignment to update.
    :return: Redirects to the courier deliveries page.
    """
    assignment = get_object_or_404(OrderAssignment, id=assignment_id)
    if request.method == "POST":
        new_status = request.POST.get("status")
        assignment.status = new_status
        assignment.save()
    return redirect(reverse("courier-deliveries"))


@login_required
def report_issue(request, assignment_id):
    """
    Renders a form for a courier to report an issue with an order assignment.
    On POST, creates or updates a DeliveryIssue and marks the assignment as 'issue_reported'.

    :param request: Django HttpRequest object.
    :param assignment_id: The ID of the OrderAssignment to report an issue for.
    :return: Renders the report issue page or redirects after a successful POST.
    """
    assignment = get_object_or_404(OrderAssignment, id=assignment_id)
    if request.method == "POST":
        issue_description = request.POST.get("issue_description", "").strip()
        delivery_issue, created = DeliveryIssue.objects.get_or_create(
            order_assignment=assignment
        )
        delivery_issue.issue_description = issue_description
        delivery_issue.save()
        assignment.status = "issue_reported"
        assignment.save()
        return redirect(reverse("courier-deliveries"))
    context = {
        "assignment": assignment,
    }
    return render(request, "courier/report_issue.html", context)
