from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.models.user import User as CustomUser
from auths.views import _redirect_to_profile
from core.utils.decorators import allowed_roles


@login_required
@allowed_roles(["seller"])
def update_shop_name(request):
    custom_user = CustomUser.objects.get(email=request.user.email)
    shop = custom_user.shops.get()

    if request.method != "POST":
        return _redirect_to_profile(custom_user)

    new_shop_name = request.POST.get("new_shop_name")

    if not new_shop_name:
        messages.error(request, "Please provide a new shop name")
        return _redirect_to_profile(custom_user)

    try:
        shop.name = new_shop_name
        shop.save()

        messages.success(request, "Shop name updated successfully")
        return _redirect_to_profile(custom_user)
    except Exception as e:
        messages.error(request, f"Failed to update shop name: {str(e)}")
        return _redirect_to_profile(custom_user)
