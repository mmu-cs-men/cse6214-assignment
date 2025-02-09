from django.db import models

from core.models.user import ROLE_CHOICES
from core.models.user import User


class UpgradeRequest(models.Model):
    """
    Represents a request by a user to upgrade their role.

    The `UpgradeRequest` model stores upgrade requests submitted by users
    who wish to change their roles (e.g., from buyer to seller). It tracks
    the requested role and the timestamp of the request.

    :ivar user: ForeignKey linking the upgrade request to the user making the request.
    :ivar target_role: The role that the user is requesting to upgrade to.
    :ivar requested_at: The timestamp indicating when the upgrade request was made.
    :ivar approved: Boolean indicating whether the upgrade request has been approved.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="upgrade_requests"
    )
    target_role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    requested_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Upgrade Request by {self.user.email} to {self.target_role}"
