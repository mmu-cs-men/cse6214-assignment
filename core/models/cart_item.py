from django.core.exceptions import ValidationError
from django.db import models

from core.models.book_listing import BookListing
from core.models.cart import Cart


class CartItem(models.Model):
    """
    Represents an item within a cart, linking it to a specific book listing and quantity.

    This model is used to manage the relationship between a cart and the book listings
    added to it. It ensures that the quantity of items in the cart is positive and provides
    methods for string representation and validation.

    Attributes:
        cart (ForeignKey): The cart to which this item belongs.
        book_listing (ForeignKey): The book listing associated with this cart item.
        quantity (PositiveIntegerField): The number of this item in the cart; defaults to 1.
    """

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    book_listing = models.ForeignKey(
        BookListing, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)

    def clean(self):
        """
        Validates the `quantity` attribute of an instance. Ensures that the quantity
        is greater than zero and raises a `ValidationError` if the condition is not met.

        Raises:
            ValidationError: Raised if the `quantity` attribute is less than or
            equal to zero. The error provides details indicating that the quantity
            must be greater than zero.
        """
        if self.quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be greater than zero."})

    def save(self, *args, **kwargs):
        """
        Summary:
        Saves the current instance after performing validation. Any extra arguments
        passed are forwarded to the parent class's `save` method.

        Args:
            args: Positional arguments passed to the save method. These are forwarded
                  to the parent class's save implementation.
            kwargs: Keyword arguments passed to the save method. These are forwarded
                    to the parent class's save implementation.

        Raises:
            Any exception raised by the `clean` method if validation fails.
        """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.book_listing.title} in Cart {self.cart.id}"
