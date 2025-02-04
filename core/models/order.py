from django.db import models

from core.models.user import User


class Order(models.Model):
    """
    Represents an order placed by a user in the system.

    This class is used to store details about an order including the user who
    placed it, its status, placement timestamp, and the total price. The status
    can be one of predefined choices including pending, completed, or cancelled.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    placed_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.id} for {self.user.email} - {self.status}"
