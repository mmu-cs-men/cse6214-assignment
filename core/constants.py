"""
This file contains predefined choice constraints used across the application models.
These choices ensure consistency and reusability for fields that require fixed options, such as roles,
item conditions, and process statuses.

Definitions:
- ROLE_CHOICES: User roles within the system (e.g., Buyer, Seller).
- CONDITION_CHOICES: Represents item conditions (e.g., Brand New, Used).
- STATUS_CHOICES: Indicates process states (e.g., Pending, Completed).

These choices are typically used in Django model fields via the `choices` argument to enforce valid inputs.
"""

ROLE_CHOICES = [
    ("buyer", "Buyer"),
    ("seller", "Seller"),
    ("admin", "Admin"),
    ("courier", "Courier"),
]

CONDITION_CHOICES = [
    ("brand_new", "Brand New"),
    ("like_new", "Like New"),
    ("used", "Used"),
    ("well_used", "Well Used"),
    ("tattered", "Tattered"),
]

STATUS_CHOICES = [
    ("pending", "Pending"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
]

RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1 to 5 rating scaler
