"""
Views for managing courier deliveries.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from core.models.delivery_issue import DeliveryIssue
from core.models.order import Order
from core.models.order_assignment import OrderAssignment
from core.models.user import User
from core.utils.decorators import allowed_roles
import uuid


@login_required
@allowed_roles(["courier"])
def deliveries_page(request):
    """
    Renders a page showing available orders (ready to ship with no assignment)
    and the logged-in courier's assignments.
    """
    # Try to get the email from request.user; if not present, assume request.user is the email string.
    try:
        user_email = request.user.email
    except AttributeError:
        user_email = request.user  # Fallback if request.user is a string

    # Retrieve the proper User instance using the email.
    current_user = get_object_or_404(User, email=user_email)

    # Available orders: orders that are ready_to_ship and have no assignment.
    available_orders = Order.objects.filter(
        status="ready_to_ship", order_assignment__isnull=True
    ).order_by("-placed_at")

    # My deliveries: order assignments for which the courier is the logged-in user.
    my_assignments = OrderAssignment.objects.filter(courier=current_user).order_by(
        "-updated_at"
    )

    context = {
        "pending_orders": available_orders,  # Keep the template variable name for now
        "my_assignments": my_assignments,
    }
    return render(request, "courier/deliveries.html", context)


@login_required
@allowed_roles(["courier"])
def accept_order(request, order_id):
    """
    Handles accepting an order. Creates an OrderAssignment for the order
    and updates its status to 'shipped'.
    """
    order = get_object_or_404(
        Order, id=order_id, status="ready_to_ship", order_assignment__isnull=True
    )

    # Retrieve a proper User instance using the email from request.user
    try:
        user_email = request.user.email
    except AttributeError:
        user_email = request.user  # Fallback if request.user is a string
    current_user = get_object_or_404(User, email=user_email)

    OrderAssignment.objects.create(order=order, courier=current_user)
    order.status = "shipped"
    order.save()
    return redirect(reverse("courier-deliveries"))


@login_required
@allowed_roles(["courier"])
def update_assignment(request, assignment_id):
    """
    Handles updating an existing assignment.
    If the action is 'unaccept', it deletes the assignment and sets the order status to 'ready_to_ship'.
    If the action is 'complete', it updates the order status to 'completed'.
    """
    # Retrieve a proper User instance using request.user.email, similar to the buyer view
    try:
        user_email = request.user.email
    except AttributeError:
        user_email = request.user  # fallback if request.user is a string

    current_user = get_object_or_404(User, email=user_email)

    # Query the assignment ensuring the courier is the proper user instance.
    assignment = get_object_or_404(
        OrderAssignment, id=assignment_id, courier=current_user
    )

    if request.method == "POST":
        action = request.POST.get("action")
        order = assignment.order
        if action == "unaccept":
            assignment.delete()
            order.status = "ready_to_ship"
            order.save()
        elif action == "complete":
            order.status = "completed"
            order.save()
    return redirect(reverse("courier-deliveries"))


@login_required
@allowed_roles(["courier"])
def report_issue(request, assignment_id):
    """
    Renders a form for a courier to report an issue with an order assignment.
    On POST, creates or updates the DeliveryIssue.
    Displays a success message when the issue is reported.

    :param request: Django HttpRequest object.
    :param assignment_id: The ID of the OrderAssignment to report an issue for.
    :return: Renders the report issue page on GET, or redirects to the deliveries page on POST.
    """
    # Retrieve a proper User instance using the email from request.user
    try:
        user_email = request.user.email
    except AttributeError:
        user_email = request.user  # Fallback if request.user is a string
    current_user = get_object_or_404(User, email=user_email)

    # Ensure that the assignment belongs to the current courier.
    assignment = get_object_or_404(
        OrderAssignment, id=assignment_id, courier=current_user
    )

    if request.method == "POST":
        # Verify the form token
        form_token = request.POST.get("form_token")
        session_token = request.session.get(f"report_issue_token_{assignment_id}")

        if not form_token or not session_token or form_token != session_token:
            # Silently ignore duplicate/invalid submissions
            return redirect("courier-deliveries")

        # Clear the token to prevent reuse
        request.session.pop(f"report_issue_token_{assignment_id}", None)

        issue_description = request.POST.get("issue_description", "").strip()
        if not issue_description:
            messages.error(request, "Please provide a description for the issue.")
            return redirect(reverse("courier-report-issue", args=[assignment_id]))

        # Create or update the DeliveryIssue for this assignment.
        delivery_issue, created = DeliveryIssue.objects.get_or_create(
            order_assignment=assignment
        )
        delivery_issue.issue_description = issue_description
        delivery_issue.save()

        messages.success(request, "Issue reported successfully!")
        return redirect(reverse("courier-deliveries"))

    # Try to get existing delivery issue
    try:
        delivery_issue = DeliveryIssue.objects.get(order_assignment=assignment)
        existing_description = delivery_issue.issue_description
    except DeliveryIssue.DoesNotExist:
        existing_description = ""

    # Generate a new token for the form
    form_token = str(uuid.uuid4())
    request.session[f"report_issue_token_{assignment_id}"] = form_token

    context = {
        "assignment": assignment,
        "existing_description": existing_description,
        "form_token": form_token,
    }
    return render(request, "courier/report_issue.html", context)
