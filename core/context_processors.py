from core.models.user import User


def user_data(request):
    """
    Context processor to add user data to all templates
    """
    if request.user.is_authenticated:
        try:
            user = User.objects.get(email=request.user.email)
            return {"custom_user": user}
        except User.DoesNotExist:
            return {}
    return {}
