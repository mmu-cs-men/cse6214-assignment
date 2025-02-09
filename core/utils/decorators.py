from django.http import HttpResponseForbidden
from functools import wraps
from core.constants import ROLE_CHOICES
from core.models.user import User as CustomUser


def allowed_roles(roles):
    """
    Restricts access to views based on user roles.

    This decorator checks if the authenticated user has one of the specified roles
    before allowing access to the decorated view. It works with the custom User model's
    role field, which can be one of the roles defined in the ROLE_CHOICES list in core/constants.py.

    :param roles: A list of role names that are allowed to access the view. Must match the role choices defined in ROLE_CHOICES.
    :return: A decorated view function that includes role-based access control
    :raises: HttpResponseForbidden if the user is not authenticated or doesn't have the required role
    :raises: ValueError if any of the specified roles are not valid according to ROLE_CHOICES

    Example::

        @allowed_roles(['seller', 'admin'])
        def seller_dashboard(request):
            # Only users with 'seller' or 'admin' roles can access this view
            pass
    """

    # Validate that all specified roles are valid
    valid_roles = [role[0] for role in ROLE_CHOICES]
    for role in roles:
        if role not in valid_roles:
            raise ValueError(
                f"Invalid role: {role}. Valid roles are: {', '.join(valid_roles)}"
            )

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden(
                    "You must be logged in to access this page."
                )

            try:
                custom_user = CustomUser.objects.get(email=request.user.email)
                if custom_user.role not in roles:
                    allowed_roles_str = ", ".join(roles)
                    return HttpResponseForbidden(
                        f"Access denied. This page requires one of the following roles: {allowed_roles_str}. "
                        f"Your current role is: {custom_user.role}"
                    )
                return view_func(request, *args, **kwargs)
            except CustomUser.DoesNotExist:
                return HttpResponseForbidden(
                    "Custom user not found. This is a system error - please contact support."
                )

        return wrapper

    return decorator
