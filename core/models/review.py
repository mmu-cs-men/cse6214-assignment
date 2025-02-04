from django.db import models

from core.models.shop import Shop
from core.models.user import User


class Review(models.Model):
    """
    Model representing a review for a shop.

    :ivar shop: ForeignKey linking the review to a shop.
    :ivar user: ForeignKey linking the review to a user.
    :ivar rating: IntegerField for the rating of the shop, restricted to a 1 to 5 scale.
    :ivar comment: TextField for additional feedback or remarks.
    :ivar created_at: DateTimeField automatically set to the timestamp when the review is created.
    """

    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1 to 5 rating scale

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.email} for {self.shop.name} - {self.rating}/5"
