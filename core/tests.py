from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from core.models.cart import Cart
from core.models.order import Order
from core.models.shop import Shop
from core.models.upgrade_request import UpgradeRequest
from core.models.user import User


# Create your tests here.


class UserModelTest(TestCase):
    """Tests for the User model

    Test Cases:
    - Successful creation of a user with an email, name, and role.
    - Validation to ensure a user must have an email.
    - Validation to ensure a user must have a name.
    - Verification that the default role is 'buyer' when no role is specified.
    - Constraint enforcement ensuring emails are unique.
    - Validation to ensure that only allowed roles can be assigned to a user.
    - String representation of a user should return the email.
    """

    def setUp(self):
        """Create a sample user for testing"""
        self.user = User.objects.create(
            email="testuser@example.com", name="Test User", role="buyer"
        )

    def test_user_creation(self):
        """Test if a user is created successfully."""
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertEqual(self.user.name, "Test User")
        self.assertEqual(self.user.role, "buyer")

    def test_email_required(self):
        """Test that a user must have an email."""
        user = User(name="No Email", role="seller")
        with self.assertRaises(ValidationError):
            user.full_clean()  # This explicitly triggers field validation

    def test_default_role(self):
        """Test that the default role is 'buyer'."""
        new_user = User.objects.create(email="new@example.com", name="New User")
        self.assertEqual(new_user.role, "buyer")

    def test_unique_email(self):
        """Test that emails must be unique."""
        with self.assertRaises(IntegrityError):
            User.objects.create(
                email="testuser@example.com", name="Duplicate User", role="seller"
            )

    def test_name_required(self):
        """Test that a user must have a name."""
        user = User(email="no_name@example.com", role="buyer")
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_invalid_role(self):
        """Test that an invalid role is not allowed."""
        user = User(
            email="invalid_role@example.com", name="Test User", role="invalid_role"
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_user_str(self):
        """Test the user string representation."""
        self.assertEqual(str(self.user), self.user.email)


class ShopModelTest(TestCase):
    """
    Test case for testing the Shop model.

    Test Cases:
    - Successful creation of a shop with a name and associated user.
    - Validation to ensure a shop must have a name.
    - Validation to ensure a shop must be linked to a user.
    - Verification of the shop's string representation.
    - Constraint enforcement to ensure that deleting a user also deletes their shop (CASCADE).
    - Validation to ensure a user can own multiple shops.
    """

    def setUp(self):
        """Create a sample user for testing"""
        self.user = User.objects.create(
            email="seller@example.com", name="Seller User", role="seller"
        )

    def test_shop_creation(self):
        """Test if a shop is created successfully."""
        shop = Shop.objects.create(name="My Bookstore", user=self.user)
        self.assertEqual(shop.name, "My Bookstore")
        self.assertEqual(shop.user, self.user)

    def test_name_required(self):
        """Test that a shop must have a name."""
        shop = Shop(user=self.user)
        with self.assertRaises(ValidationError):
            shop.full_clean()

    def test_shop_must_have_user(self):
        """Test that a shop must be linked to a user."""
        shop = Shop(name="No Owner Shop", user=None)
        with self.assertRaises(ValidationError):
            shop.full_clean()

    def test_shop_string_representation(self):
        """Test the shop string representation."""
        shop = Shop.objects.create(name="My Bookstore", user=self.user)
        self.assertEqual(str(shop), "My Bookstore")  # FIXED: Matching actual name

    def test_deleting_user_deletes_shop(self):
        """Test that deleting a user also deletes their shop (CASCADE)"""
        shop = Shop.objects.create(name="My Bookstore", user=self.user)
        self.user.delete()

        with self.assertRaises(Shop.DoesNotExist):  # The shop should be gone
            Shop.objects.get(id=shop.id)  # FIXED: Use 'id' instead of 'shop_id'

    def test_user_can_have_multiple_shops(self):
        """Test that a user can own multiple shops"""
        shop1 = Shop.objects.create(name="Shop 1", user=self.user)  # FIXED
        shop2 = Shop.objects.create(name="Shop 2", user=self.user)  # FIXED

        self.assertEqual(self.user.shops.count(), 2)  # Check total shops
        self.assertIn(shop1, self.user.shops.all())  # Verify shop1 is in queryset
        self.assertIn(shop2, self.user.shops.all())  # Verify shop2 is in queryset


class CartModelTest(TestCase):
    """
    A test case for validating the Cart model functionality in a Django application.

    Test Cases:
    - Successful creation of a cart associated with a user.
    - Validation to ensure a cart must be linked to a user.
    - Constraint enforcement to ensure that deleting a user also deletes their cart (CASCADE).
    - Validation to ensure carts are retrieved in the order they were created.
    - Verification that a user can have multiple carts.
    - Verification of the cart's string representation.
    """

    def setUp(self):
        """Create a sample user for testing"""
        self.user = User.objects.create(
            email="buyer@example.com", name="Buyer User", role="buyer"
        )

    def test_cart_creation(self):
        """Test if a cart is created successfully."""
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(cart.user, self.user)
        self.assertIsNotNone(cart.created_at)  # Ensure timestamp is set

    def test_cart_must_have_user(self):
        """Test that a cart must be linked to a user."""
        cart = Cart(user=None)
        with self.assertRaises(ValidationError):
            cart.full_clean()

    def test_deleting_user_deletes_cart(self):
        """Test that deleting a user also deletes their cart (CASCADE)"""
        cart = Cart.objects.create(user=self.user)
        self.user.delete()

        with self.assertRaises(Cart.DoesNotExist):  # The cart should be gone
            Cart.objects.get(id=cart.id)

    def test_carts_are_ordered_by_creation_date(self):
        """Test that carts are retrieved in the order they were created"""
        cart1 = Cart.objects.create(user=self.user)
        cart2 = Cart.objects.create(user=self.user)

        carts = list(Cart.objects.filter(user=self.user).order_by("created_at"))
        self.assertEqual(carts, [cart1, cart2])  # Verify correct order

    def test_user_can_have_multiple_carts(self):
        """Test that a user can have multiple carts"""
        cart1 = Cart.objects.create(user=self.user)
        cart2 = Cart.objects.create(user=self.user)

        self.assertEqual(self.user.carts.count(), 2)  # Check total carts
        self.assertIn(cart1, self.user.carts.all())  # Verify cart1 exists
        self.assertIn(cart2, self.user.carts.all())  # Verify cart2 exists

    def test_cart_str_representation(self):
        """Test the cart string representation"""
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(str(cart), f"Cart {cart.id} for {self.user.email}")


class OrderModelTest(TestCase):
    """
    Test case suite for testing the `Order` model.

     Test Cases:
    - Successful creation of an order with an associated user and total price.
    - Validation to ensure an order must be linked to a user.
    - Verification that the default status of an order is 'pending'.
    - Constraint enforcement to ensure that deleting a user also deletes their orders (CASCADE).
    - Verification that an order's timestamp is correctly set upon creation.

    """

    def setUp(self):
        """Create a sample user for testing"""
        self.user = User.objects.create(
            email="buyer@example.com", name="Buyer User", role="buyer"
        )

    def test_order_creation(self):
        """Test if an order is created successfully."""
        order = Order.objects.create(user=self.user, total_price=100.50)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, "pending")  # Default status
        self.assertIsNotNone(order.placed_at)  # Ensure timestamp is set

    def test_order_must_have_user(self):
        """Test that an order must be linked to a user."""
        order = Order(user=None, total_price=50.00)
        with self.assertRaises(ValidationError):
            order.full_clean()

    def test_order_default_status(self):
        """Test that the default order status is 'pending'."""
        order = Order.objects.create(user=self.user, total_price=75.00)
        self.assertEqual(order.status, "pending")

    def test_deleting_user_deletes_order(self):
        """Test that deleting a user also deletes their orders (CASCADE)"""
        order = Order.objects.create(user=self.user, total_price=150.00)
        self.user.delete()

        with self.assertRaises(Order.DoesNotExist):  # The order should be gone
            Order.objects.get(id=order.id)


class UpgradeRequestModelTest(TestCase):
    """Tests for the UpgradeRequestModel

    Test Cases:
    - Successful creation of an upgrade request with an associated user and target role.
    - Validation to ensure an upgrade request must be linked to a user.
    - Validation to ensure an upgrade request has a valid target role.
    - Constraint enforcement to ensure that deleting a user also deletes their upgrade requests (CASCADE).
    - Verification that an upgrade request's timestamp is correctly set upon creation.
    """

    def setUp(self):
        """Create a sample user for testing"""
        self.user = User.objects.create(
            email="user@example.com", name="Test User", role="buyer"
        )

    def test_upgrade_request_creation(self):
        """Test if an upgrade request is created successfully."""
        request = UpgradeRequest.objects.create(user=self.user, target_role="seller")
        self.assertEqual(request.user, self.user)
        self.assertEqual(request.target_role, "seller")
        self.assertIsNotNone(request.requested_at)  # Ensure timestamp is set

    def test_upgrade_request_must_have_user(self):
        """Test that an upgrade request must be linked to a user."""
        request = UpgradeRequest(user=None, target_role="seller")
        with self.assertRaises(ValidationError):
            request.full_clean()

    def test_upgrade_request_must_have_valid_role(self):
        """Test that an upgrade request must have a valid role."""
        request = UpgradeRequest(user=self.user, target_role="invalid_role")
        with self.assertRaises(ValidationError):
            request.full_clean()

    def test_deleting_user_deletes_upgrade_request(self):
        """Test that deleting a user also deletes their upgrade requests (CASCADE)"""
        request = UpgradeRequest.objects.create(user=self.user, target_role="seller")
        self.user.delete()

        with self.assertRaises(
            UpgradeRequest.DoesNotExist
        ):  # The request should be gone
            UpgradeRequest.objects.get(id=request.id)
