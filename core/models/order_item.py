from django.core.exceptions import ValidationError
from django.db import models

from core.models.book_listing import BookListing
from core.models.order import Order


class OrderItem(models.Model):
    """
    Represents an item inside an order.

    Each order item is linked to an `Order` and a `BookListing`, containing
    details about the quantity of books purchased and the price at which
    they were bought.

    :ivar order: ForeignKey linking the order item to an order.
    :vartype order: Order

    :ivar book_listing: ForeignKey linking the order item to a book listing.
     book_listing: BookListing

    :ivar quantity: The number of copies of the book in the order.
    quantity: int

    :ivar purchase_price: The price at which the book was purchased.
     purchase_price: float
    """

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    book_listing = models.ForeignKey(
        BookListing, on_delete=models.CASCADE, related_name="order_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self) -> None:
        """
        Validates the model's constraints before saving.

        This method ensures that both `quantity` and `purchase_price` have valid values.
        - `quantity` must be greater than zero.
        - `purchase_price` must be greater than zero.

        If either value is invalid, a `ValidationError` is raised.

        :raises ValidationError: If `quantity` is less than or equal to zero.
        :raises ValidationError: If `purchase_price` is less than or equal to zero.
        """
        if self.quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be greater than zero."})
        if self.purchase_price <= 0:
            raise ValidationError(
                {"purchase_price": "Purchase price must be greater than zero."}
            )

    def save(self, *args, **kwargs) -> None:
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

    def __str__(self) -> str:
        return f"{self.quantity}x {self.book_listing.title} in Order {self.order.id} - ${self.purchase_price}"
