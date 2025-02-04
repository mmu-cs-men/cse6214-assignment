from django.db import models

from core.models.user import User


class Shop(models.Model):
    """
    Represents a shop owned by a user.

    The `Shop` model stores information about a seller's shop, including
    the shop's name and the user who owns it.

    :ivar name: The name of the shop.
    :ivar user: ForeignKey linking the shop to its owner.
    """

    name = models.CharField(max_length=255, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shops")

    def __str__(self):
        return self.name
