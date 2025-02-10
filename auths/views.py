from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import reverse
from core.models.user import User as CustomUser
from django.http import Http404
from django.contrib.auth.decorators import login_required
from core.models.upgrade_request import UpgradeRequest
import re


def _redirect_based_on_role(custom_user):
    """Helper function to redirect users based on their role."""
    role_to_url = {
        "buyer": "buyer-landing",
        "seller": "seller-dashboard",
        "courier": "courier-deliveries",
        "admin": "admin",
    }

    if custom_user.role not in role_to_url:
        raise Http404(
            "Invalid user role. This shouldn't have happened. Find your nearest developer"
        )

    return redirect(reverse(role_to_url[custom_user.role]))


def _check_courier_approval(request, custom_user):
    """Helper function to check if a courier's upgrade request is approved.
    Returns True if the user is approved or not a courier, False otherwise."""
    if custom_user.role == "courier":
        try:
            upgrade_request = UpgradeRequest.objects.get(
                user=custom_user, target_role="courier"
            )
            if not upgrade_request.approved:
                messages.info(
                    request,
                    "Your courier application is still pending approval. Please check back later.",
                )
                return False
        except UpgradeRequest.DoesNotExist:
            messages.warning(
                request,
                "Somehow, you are a courier but don't have an upgrade request. Find your nearest developer.",
            )
            return False
    return True


def validate_password_strength(password):
    """
    Validate that password meets strength requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    - Contains at least one special character
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True


def login_view(request):
    # If user is already authenticated, redirect them to their appropriate page
    if request.user.is_authenticated:
        # Check if user is staff/superuser first
        if request.user.is_staff or request.user.is_superuser:
            return redirect("/admin/")

        try:
            custom_user = CustomUser.objects.get(email=request.user.email)

            if not _check_courier_approval(request, custom_user):
                logout(request)
                return render(request, "login.html")

            return _redirect_based_on_role(custom_user)
        except CustomUser.DoesNotExist:
            messages.error(
                request,
                "Custom user does not exist. This is a logic error and shouldn't have happened. Find your nearest developer",
            )

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            auth_user = User.objects.get(email=email)
            user = authenticate(request, username=auth_user.username, password=password)
            if user is not None:
                # Check if user is staff/superuser first
                if user.is_staff or user.is_superuser:
                    login(request, user)
                    return redirect("/admin/")

                custom_user = CustomUser.objects.get(email=email)

                if not _check_courier_approval(request, custom_user):
                    return render(request, "login.html")

                login(request, user)
                return _redirect_based_on_role(custom_user)
            else:
                messages.error(request, "Invalid password")
        except User.DoesNotExist:
            messages.error(request, "No account found with this email")
        except CustomUser.DoesNotExist:
            # Check if the user might be a staff/admin user without a CustomUser
            try:
                auth_user = User.objects.get(email=email)
                if auth_user.is_staff or auth_user.is_superuser:
                    user = authenticate(
                        request, username=auth_user.username, password=password
                    )
                    if user is not None:
                        login(request, user)
                        return redirect("/admin/")
                messages.error(request, "Invalid credentials")
            except User.DoesNotExist:
                messages.error(
                    request,
                    "No account found with this email",
                )

    return render(request, "login.html")


def register_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "register.html")

        if not validate_password_strength(password):
            messages.error(request, "Password does not meet strength requirements")
            return render(request, "register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, "register.html")

        try:
            # Create unique username using counter
            username = email.split("@")[0]  # Use part before @ as username
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            # Create built-in user
            auth_user = User.objects.create_user(
                username=username, email=email, password=password
            )

            # Create custom user with role
            custom_user = CustomUser.objects.create(email=email, name=name, role=role)

            # Create upgrade request for courier with approved=False
            if role == "courier":
                UpgradeRequest.objects.create(
                    user=custom_user, target_role="courier", approved=False
                )
                messages.info(
                    request,
                    "Your courier account request has been submitted for review. Please check periodically for approval by signing in.",
                )
                return redirect(reverse("login"))

            user = authenticate(request, username=auth_user.username, password=password)
            if user is not None:
                login(request, user)

                if role == "buyer":
                    return redirect(reverse("buyer-landing"))

            return redirect(reverse("login"))

        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return render(request, "register.html")

    return render(request, "register.html")


def logout_view(request):
    logout(request)
    return redirect(reverse("login"))


def _redirect_to_profile(custom_user):
    role_to_url = {
        "buyer": "buyer-profile",
        "seller": "seller-profile",
        "courier": "courier-profile",
        "admin": "admin-profile",
    }
    return redirect(reverse(role_to_url[custom_user.role]))


@login_required
def update_email(request):
    custom_user = CustomUser.objects.get(email=request.user.email)

    if request.method != "POST":
        return _redirect_to_profile(custom_user)

    new_email = request.POST.get("new_email")

    if not new_email:
        messages.error(request, "Please provide a new email address")
        return _redirect_to_profile(custom_user)

    # Check if email is already taken
    if User.objects.exclude(id=request.user.id).filter(email=new_email).exists():
        messages.error(request, "This email is already registered")
        return _redirect_to_profile(custom_user)

    try:
        # Update Django auth user email
        auth_user = request.user
        auth_user.email = new_email
        auth_user.save()

        # Update custom user email
        custom_user.email = new_email
        custom_user.save()

        messages.success(request, "Email updated successfully")
        return _redirect_to_profile(custom_user)
    except Exception as e:
        messages.error(request, f"Failed to update email: {str(e)}")
        return _redirect_to_profile(custom_user)


@login_required
def change_password(request):
    custom_user = CustomUser.objects.get(email=request.user.email)

    if request.method != "POST":
        return _redirect_to_profile(custom_user)

    current_password = request.POST.get("current_password")
    new_password = request.POST.get("new_password")
    confirm_password = request.POST.get("confirm_password")

    if not request.user.check_password(current_password):
        messages.error(request, "Current password is incorrect")
        return _redirect_to_profile(custom_user)

    if new_password != confirm_password:
        messages.error(request, "New passwords do not match")
        return _redirect_to_profile(custom_user)

    try:
        request.user.set_password(new_password)
        request.user.save()
        # Re-authenticate user to prevent logout
        user = authenticate(
            request, username=request.user.username, password=new_password
        )
        if user is not None:
            login(request, user)
            messages.success(request, "Password changed successfully")
            return _redirect_to_profile(custom_user)
    except Exception as e:
        messages.error(request, f"Failed to change password: {str(e)}")
        return _redirect_to_profile(custom_user)
