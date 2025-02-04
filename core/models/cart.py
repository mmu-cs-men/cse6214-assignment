from django.db import models

from core.models.user import User


class Cart(models.Model):
    """
    Represents a shopping cart associated with a user.

    The cart model stores items that a user intends to purchase. Each cart
    is linked to a specific user and tracks when it was created.

    :ivar user: ForeignKey linking the cart to a user.
    :ivar created_at: The timestamp indicating when the cart was created.

    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user.email}"
