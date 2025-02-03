from django.core.exceptions import ValidationError
from django.test import TestCase

from core.models.user import User


# Create your tests here.


class UserModelTest(TestCase):
    """
    Create a sample user for testing.

    Summary:
    This method initializes a User instance to be used across
    multiple test cases. The sample user contains predefined
    values for email, name, and role attributes.
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
