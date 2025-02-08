from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import reverse
from core.models.user import User as CustomUser
from django.http import Http404


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            auth_user = User.objects.get(email=email)
            user = authenticate(request, username=auth_user.username, password=password)
            if user is not None:
                login(request, user)
                custom_user = CustomUser.objects.get(email=email)

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
