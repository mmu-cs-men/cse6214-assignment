from django.db import models

from core.constants import ROLE_CHOICES


class User(models.Model):
    """
    Represents a user in the system.

    This model defines the attributes and roles of users within the platform. Each user
    has a unique email, a name, and a specific role that determines their permissions
    and actions.

    :ivar email: A unique email address used for authentication and identification.
     email: str

    :ivar name: The full name of the user.
     name: str

    :ivar role: The role of the user within the system, chosen from predefined options
        ('buyer', 'seller', 'admin', 'courier'). Defaults to 'buyer'.
    role: str
    """

    email = models.EmailField(unique=True, null=False, blank=False)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="buyer")

    def __str__(self):
        return self.email
