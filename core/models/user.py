from django.db import models


class User(models.Model):
    """
    Represents a user entity with attributes for identification and role-based functionality.

    This class is used for managing user data within the system. It includes attributes for
    email, name, and role to distinguish different user types such as buyers, sellers, admins,
    and couriers. The role determines the user's permissions and capabilities within the system.

    Attributes:
        email (EmailField):
            The unique email address associated with the user.
        name (CharField):
            The full name of the user with a maximum length of 255 characters.
        role (CharField):
            The role of the user, which defines the users' privileges.
            The available choices are:

            - "buyer": Default role for general users.
            - "seller": Role for users managing book listings.
            - "admin": Role for system administrators
            - "courier": Role for users managing deliveries.

            Defaults to "buyer".
    """

    ROLE_CHOICES = [
        ("buyer", "Buyer"),
        ("seller", "Seller"),
        ("admin", "Admin"),
        ("courier", "Courier"),
    ]

    email = models.EmailField(unique=True, null=False, blank=False)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="buyer")

    def __str__(self):
        return self.email
