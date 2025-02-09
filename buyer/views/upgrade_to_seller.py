from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, reverse
from core.models.upgrade_request import UpgradeRequest
from core.models.user import User as CustomUser
from core.utils.decorators import allowed_roles

@login_required
@allowed_roles(["buyer"])
def upgrade_to_seller(request):
    custom_user = CustomUser.objects.get(email=request.user.email)

    # Check if user already has a pending upgrade request
    if UpgradeRequest.objects.filter(user=custom_user, target_role="seller").exists():
        messages.info(request, "You already have a pending request to become a seller. Please wait for admin approval.")
        return redirect(reverse("buyer-landing"))

    if request.method == "POST":
        UpgradeRequest.objects.create(
            user=custom_user,
            target_role="seller"
        )
        
        messages.success(request, "Your request to become a seller has been submitted. Please check back later for approval status.")
        return redirect(reverse("buyer-landing"))

    return render(request, "buyer/upgrade_to_seller.html")
