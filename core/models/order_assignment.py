from django.db import models

from core.models.order import Order
from core.models.user import User


class OrderAssignment(models.Model):
    """
    Represents the assignment of an order to a courier for delivery.

    This model links an `Order` to a `User` (acting as a courier) and records
    the timestamp when the assignment was made.

    :ivar order: ForeignKey linking the assignment to an order.
    :ivar courier: ForeignKey linking the assignment to a courier user.
    :ivar assigned_at: The timestamp indicating when the order was assigned.
    """

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="order_assignment"
    )
    courier = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="assigned_orders"
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Order {self.order.id} assigned to {self.courier.email} on {self.assigned_at}"
