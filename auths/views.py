from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import reverse
from core.models.user import User as CustomUser
from django.http import Http404


def _redirect_based_on_role(custom_user):
    """Helper function to redirect users based on their role."""
    if custom_user.role == "buyer":
        return redirect(reverse("buyer-landing"))
    elif custom_user.role == "seller":
        return redirect(reverse("seller-dashboard"))
    elif custom_user.role == "courier":
        return redirect(reverse("courier-deliveries"))
    elif custom_user.role == "admin":
        return redirect("/admin")
    else:
        raise Http404(
            "Invalid user role. This shouldn't have happened. Find your nearest developer"
        )


def login_view(request):
    # If user is already authenticated, redirect them to their appropriate page
    if request.user.is_authenticated:
        try:
            custom_user = CustomUser.objects.get(email=request.user.email)
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
                login(request, user)
                custom_user = CustomUser.objects.get(email=email)
                return _redirect_based_on_role(custom_user)
            else:
                messages.error(request, "Invalid password")
        except User.DoesNotExist:
            messages.error(request, "No account found with this email")
        except CustomUser.DoesNotExist:
            messages.error(
                request,
                "Custom user does not exist. This is a logic error and shouldn't have happened. Find your nearest developer",
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

            # Create custom user
            custom_user = CustomUser.objects.create(email=email, name=name, role=role)

            user = authenticate(request, username=auth_user.username, password=password)
            if user is not None:
                login(request, user)

                if role == "buyer":
                    return redirect(reverse("buyer-landing"))
                elif role == "courier":
                    return redirect(reverse("courier-deliveries"))

            return redirect(reverse("login"))

        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return render(request, "register.html")

    return render(request, "register.html")


def logout_view(request):
    logout(request)
    return redirect(reverse("login"))
