from django.db import models

from core.models.user import User


class Order(models.Model):
    """
    Represents a purchase order made by a user.

    The `Order` model stores details about transactions, including the
    user who placed the order, its current status, the total price, and
    the timestamp when it was placed.

    :ivar user: ForeignKey linking the order to a user.
    :vartype user: User

    :ivar status: The status of the order (Pending, Completed, Cancelled).
    :vartype status: str

    :ivar placed_at: The timestamp indicating when the order was placed.
    :vartype placed_at: datetime

    :ivar total_price: The total amount for the order.
    :vartype total_price: float
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
