from django.db import models

from core.models.order_assignment import OrderAssignment


class DeliveryIssue(models.Model):
    """
    Represents an issue encountered during the delivery of an order.

    Each delivery issue is linked to an `OrderAssignment`, containing details
    about the problem reported and the timestamp of when it was logged.

    :ivar order_assignment: ForeignKey linking the issue to an order assignment.
    :ivar issue_description: A detailed description of the delivery issue.
    :ivar reported_at: The timestamp indicating when the issue was reported.

    """

    order_assignment = models.OneToOneField(
        OrderAssignment, on_delete=models.CASCADE, related_name="delivery_issue"
    )
    issue_description = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Issue for Order {self.order_assignment.order.id}: {self.issue_description[:50]}..."
