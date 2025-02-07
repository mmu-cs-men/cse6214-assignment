from django.db import models

from core.constants import STATUS_CHOICES
from core.models.user import User


class Order(models.Model):
    """
    Represents a purchase order made by a user.

    The `Order` model stores details about transactions, including the
    user who placed the order, its current status, the total price,
    the shipping address details, and the timestamp when it was placed.

    :ivar user: ForeignKey linking the order to a user.
    :ivar status: The status of the order (Pending, Completed, Cancelled).
    :ivar placed_at: The timestamp indicating when the order was placed.
    :ivar total_price: The total amount for the order.
    :ivar address: The street address for shipping.
    :ivar city: The city where the order is being shipped.
    :ivar state: The state or region for the shipping address.
    :ivar postal_code: The postal/zip code for shipping.
    :ivar country: The country where the order is being shipped.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    placed_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Address details
    address = models.TextField(default="Not Provided")
    city = models.CharField(max_length=100, default="Not Provided")
    state = models.CharField(max_length=100, default="Not Provided")
    postal_code = models.CharField(max_length=20, default="000000")
    country = models.CharField(max_length=100, default="Not Provided")

    def __str__(self):
        return f"Order {self.id} for {self.user.email} - {self.status}"
