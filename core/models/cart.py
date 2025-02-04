from django.db import models

from core.models.user import User


class Cart(models.Model):
    """
    Represents a shopping cart associated with a user.

    This class defines a cart model in the system that is linked to a specific user.
    Each cart stores the user it is associated with and the time it was created.
    This is typically used to manage a user's shopping process.

    Attributes:
        user (User): The user to whom the cart belongs.
        created_at (datetime): The timestamp indicating when the cart was created.

    Methods:
        __str__(): Returns a string representation of the cart including its ID
        and the email of the associated user.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user.email}"
