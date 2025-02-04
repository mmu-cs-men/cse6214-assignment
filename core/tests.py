from django.core.exceptions import ValidationError
from django.test import TestCase

from core.models.shop import Shop
from core.models.user import User


# Create your tests here.


class UserModelTest(TestCase):
    """
    Unit tests for the User model class.

    This test class provides a series of test cases to validate the behavior and integrity of the
    User model in various scenarios. It checks for the creation of users, required fields,
    default values, constraints on field uniqueness, and validation of allowed values. Additionally,
    it verifies the string representation of the User object.
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
        with self.assertRaises(Exception):  # Should raise IntegrityError
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
