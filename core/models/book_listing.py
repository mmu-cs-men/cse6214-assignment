from django.db import models

from core.constants import CONDITION_CHOICES
from core.models.shop import Shop


class BookListing(models.Model):
    """
    Model representing a second-hand book listing in the marketplace.

    :ivar shop: ForeignKey linking the listing to a shop.
    :ivar title: Title of the book.
    :ivar author: Author of the book.
    :ivar condition: Condition of the book (NEW, GOOD, FAIR).
    :ivar price: Price of the book listing.
    :ivar image: ImageField for storing raw image files.
    :ivar bought: Boolean indicating whether the book has been purchased.
    """

    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE, related_name="book_listings"
    )
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="book_images/", null=True, blank=True)
    bought = models.BooleanField(default=False)

    def __str__(self):
        return self.title
