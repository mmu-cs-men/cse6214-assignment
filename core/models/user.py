from django.db import models


class User(models.Model):
    """Represents a user in the system with specific attributes such as email, name, and role.

    This class defines a user model within the system. It includes fields for email, name,
    and role, with predefined choices for the role. The role determines the user's function
    within the system, like buyer, seller, admin, or courier. This structure allows the system
    to categorize and manage users effectively.

    Attributes:
        email (EmailField): The unique email address associated with the user.
        name (CharField): The name of the user, stored as a string with a maximum length of
            255 characters.
        role (CharField): The role of the user selected from predefined choices
            (buyer, seller, admin, courier), with "buyer" as the default selection.
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
