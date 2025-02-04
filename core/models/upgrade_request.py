from django.db import models

from core.models.user import User


class UpgradeRequest(models.Model):
    """
    Represents a request to upgrade a user's role within the system.

    This model is designed to track user-initiated upgrade requests,
    specifically capturing the user making the request, the role they
    wish to upgrade to, and the timestamp of the request. It also includes
    predefined role choices to categorize requests.

    """

    ROLE_CHOICES = [
        ("buyer", "Buyer"),
        ("seller", "Seller"),
        ("admin", "Admin"),
        ("courier", "Courier"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="upgrade_requests"
    )
    target_role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Upgrade Request by {self.user.email} to {self.target_role}"
