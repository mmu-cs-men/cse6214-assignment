from django.core.exceptions import ValidationError
from django.db import models

from core.models.book_listing import BookListing
from core.models.cart import Cart


class CartItem(models.Model):
    """
    Represents an item in a shopping cart with associations to a cart and a book listing,
    along with a specified quantity.

    This model links a `Cart` to a `BookListing` and records the quantity of the book
    listing in the cart. It ensures data integrity by validating that the quantity is
    greater than zero.

    :ivar cart: ForeignKey linking the item to a shopping cart.
    :ivar book_listing: ForeignKey linking the item to a book listing.
    :ivar quantity: The number of the specific book in the cart.
    """

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    book_listing = models.ForeignKey(
        BookListing, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)

    def clean(self):
        """
        Validates the model's constraints before saving.

        This method ensures that the quantity of an item is greater than zero.
        If the quantity is zero or negative, a `ValidationError` is raised.

        :raises ValidationError: If `quantity` is less than or equal to zero.
        """
        if self.quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be greater than zero."})

    def save(self, *args, **kwargs):
        """
        Saves the model instance after validation.

        This method overrides the default save behavior to ensure data integrity
        by calling the `clean` method before saving. It ensures that all
        validation checks are enforced before persisting the instance to the database.

        :param args: Positional arguments passed to the parent `save` method.
        :param kwargs: Keyword arguments passed to the parent `save` method.
        """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.book_listing.title} in Cart {self.cart.id}"
