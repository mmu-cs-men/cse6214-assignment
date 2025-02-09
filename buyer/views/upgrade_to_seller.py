from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, reverse
from core.models.upgrade_request import UpgradeRequest
from core.models.user import User as CustomUser
from core.utils.decorators import allowed_roles
from core.models.shop import Shop


def _handle_seller_upgrade_request(request, custom_user):
    """Helper function to handle seller upgrade requests.
    Returns True if a new request was created, False if one already exists."""
    try:
        # Check if user already has a pending upgrade request
        UpgradeRequest.objects.get(user=custom_user, target_role="seller")
        messages.info(
            request,
            "You already have a pending request to become a seller. Please wait for admin approval.",
        )
        return False
    except UpgradeRequest.DoesNotExist:
        # Create new upgrade request
        UpgradeRequest.objects.create(
            user=custom_user, target_role="seller", approved=False
        )
        messages.success(
            request,
            "Your request to become a seller has been submitted. Please check back later for approval status.",
        )
        return True


@login_required
@allowed_roles(["buyer"])
def upgrade_to_seller(request):
    custom_user = CustomUser.objects.get(email=request.user.email)

    if request.method == "GET":
        try:
            upgrade_request = UpgradeRequest.objects.get(
                user=custom_user, target_role="seller"
            )
            if upgrade_request.approved:
                # Update user role to seller if request is approved
                custom_user.role = "seller"
                custom_user.save()

                # Create a default shop for the new seller
                shop_name = f"{custom_user.name}'s Shop"
                Shop.objects.create(name=shop_name, user=custom_user)

                messages.success(
                    request,
                    "Congratulations! Your seller application has been approved. You are now a seller.",
                )
                return redirect(reverse("seller-dashboard"))
            else:
                messages.info(
                    request,
                    "You already have a pending request to become a seller. Please wait for admin approval.",
                )
                return redirect(reverse("buyer-landing"))
        except UpgradeRequest.DoesNotExist:
            pass

    if request.method == "POST":
        _handle_seller_upgrade_request(request, custom_user)
        return redirect(reverse("buyer-landing"))

    return render(request, "buyer/upgrade_to_seller.html")
