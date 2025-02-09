from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models.user import User as CustomUser
from core.utils.decorators import allowed_roles


@login_required
@allowed_roles(["seller"])
def profile_page(request):
    custom_user = CustomUser.objects.get(email=request.user.email)
    shop = custom_user.shops.get()

    context = {
        "name": custom_user.name,
        "shop_name": shop.name,
        "username": request.user.username,
        "email": request.user.email,
    }

    return render(request, "seller/profile.html", context)
