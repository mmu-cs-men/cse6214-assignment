from django.db import models

from core.models.order import Order
from core.models.user import User


class OrderAssignment(models.Model):
    """
    Represents the assignment of an order to a courier for delivery.

    This model links an Order to a courier (User) and records the assignment time.
    It also tracks the current delivery status and the last update time.

    :ivar order: OneToOneField linking the assignment to an order.
    :ivar courier: ForeignKey linking the assignment to a courier user.
    :ivar assigned_at: The timestamp when the order was assigned.
    :ivar updated_at: The timestamp when the assignment was last updated.
    """

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="order_assignment"
    )
    courier = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="assigned_orders"
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Order {self.order.id} assigned to {self.courier.email} on {self.assigned_at}"
