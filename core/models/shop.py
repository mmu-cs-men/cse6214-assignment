from django.db import models

from core.models.user import User


class Shop(models.Model):
    """
    Represents a shop entity within the system.

    This class is a Django model for storing and managing information about a shop. It includes
    basic attributes such as the shop's name and the user associated with it. The `Shop` class
    is tied to Django's ORM for database operations, providing functionalities to create, update,
    and manage shop records in the database.
    """

    name = models.CharField(max_length=255, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shops")

    def __str__(self):
        return self.name
