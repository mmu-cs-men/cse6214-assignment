from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from core.models.book_listing import BookListing
from core.models.cart import Cart
from core.models.cart_item import CartItem
from core.models.delivery_issue import DeliveryIssue
from core.models.order import Order
from core.models.order_assignment import OrderAssignment
from core.models.order_item import OrderItem
from core.models.review import Review
from core.models.shop import Shop
from core.models.upgrade_request import UpgradeRequest
from core.models.user import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os


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
            user.full_clean()

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
        self.assertEqual(str(shop), "My Bookstore")

    def test_deleting_user_deletes_shop(self):
        """Test that deleting a user also deletes their shop (CASCADE)"""
        shop = Shop.objects.create(name="My Bookstore", user=self.user)
        self.user.delete()

        with self.assertRaises(Shop.DoesNotExist):
            Shop.objects.get(id=shop.id)

    def test_user_can_have_multiple_shops(self):
        """Test that a user can own multiple shops"""
        shop1 = Shop.objects.create(name="Shop 1", user=self.user)
        shop2 = Shop.objects.create(name="Shop 2", user=self.user)

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
        """Test that deleting a user al so deletes their upgrade requests (CASCADE)"""
        request = UpgradeRequest.objects.create(user=self.user, target_role="seller")
        self.user.delete()

        with self.assertRaises(
            UpgradeRequest.DoesNotExist
        ):  # The request should be gone
            UpgradeRequest.objects.get(id=request.id)


class BookListingModelTest(TestCase):
    """Tests for the BookListingModel functionality.

    This test suite verifies the creation, validation, and deletion behavior of the
    BookListing model in relation to shops. It ensures that listings are created
    correctly, validations function as expected for required attributes, and cascading
    deletions work as intended when a related shop is removed.

    Test Cases:
    - Book listing creation and proper linking to a shop.
    - Required relation between book listings and shops.
    - Validation of acceptable book condition values.
    - Cascading deletion of book listings when their related shop is deleted.
    """

    def setUp(self):
        """Create a sample shop for testing"""
        self.user = User.objects.create(
            email="seller@example.com", name="Seller", role="seller"
        )
        self.shop = Shop.objects.create(name="Book Haven", user=self.user)

    def test_book_listing_creation(self):
        """Test if a book listing is created successfully."""
        listing = BookListing.objects.create(
            shop=self.shop,
            title="Django for Beginners",
            author="William S. Vincent",
            condition="good",
            price=29.99,
        )
        self.assertEqual(listing.shop, self.shop)
        self.assertEqual(listing.title, "Django for Beginners")
        self.assertEqual(listing.condition, "good")

    def test_book_listing_must_have_shop(self):
        """Test that a book listing must be linked to a shop."""
        listing = BookListing(
            title="No Shop Book", author="Unknown", condition="fair", price=10.00
        )
        with self.assertRaises(ValidationError):
            listing.full_clean()

    def test_book_listing_must_have_valid_condition(self):
        """Test that a book listing must have a valid condition."""
        listing = BookListing(
            shop=self.shop,
            title="Invalid Condition Book",
            author="Fake",
            condition="bad",
            price=5.00,
        )
        with self.assertRaises(ValidationError):
            listing.full_clean()

    def test_deleting_shop_deletes_book_listings(self):
        """Test that deleting a shop also deletes its book listings (CASCADE)"""
        listing = BookListing.objects.create(
            shop=self.shop,
            title="Python Basics",
            author="John Doe",
            condition="new",
            price=19.99,
        )
        self.shop.delete()

        with self.assertRaises(BookListing.DoesNotExist):  # The listing should be gone
            BookListing.objects.get(id=listing.id)

    def test_book_listing_image_assignment(self):
        """Test that a book listing can be created with an image file."""
        with open(os.path.join(settings.MEDIA_ROOT, "test_img.jpg"), "rb") as f:
            image_data = f.read()

        image_file = SimpleUploadedFile(
            "test_img.jpg", image_data, content_type="image/jpeg"
        )
        listing = BookListing.objects.create(
            shop=self.shop,
            title="Test Image Book",
            author="Image Author",
            condition="used",
            price=15.00,
            image=image_file,
        )
        self.assertIsNotNone(listing.image)
        self.assertIn("test_img.jpg", listing.image.name)

    def test_book_listing_without_image(self):
        """Test that a book listing created without an image remains with an empty image field."""
        listing = BookListing.objects.create(
            shop=self.shop,
            title="Test No Image Book",
            author="No Image Author",
            condition="tattered",
            price=20.00,
        )
        # If no image is uploaded, the field should be empty (evaluates to False)
        self.assertFalse(listing.image)


class ReviewModelTest(TestCase):
    """Tests for the ReviewModel functionality.

    This test suite verifies the creation, validation, and deletion behavior of the
    Review model. It ensures that reviews are created correctly, validations function
    as expected for required attributes and constraints, and cascading deletions
    work as intended when a related shop or user is removed.

    Test Cases:
    - Creation of a review and proper linking to a shop and user.
    - Validation of the rating to ensure it falls between acceptable range (1-5).
    - Validation that reviews are linked to both a shop and a user.
    - Cascading deletion of reviews when their related shop is deleted.
    - Cascading deletion of reviews when the associated user is deleted.
    """

    def setUp(self):
        """Create a sample shop and user for testing"""
        self.user = User.objects.create(
            email="buyer@example.com", name="Buyer User", role="buyer"
        )
        self.shop = Shop.objects.create(name="Tech Haven", user=self.user)

    def test_review_creation(self):
        """Test if a review is created successfully."""
        review = Review.objects.create(
            shop=self.shop, user=self.user, rating=5, comment="Excellent service!"
        )
        self.assertEqual(review.shop, self.shop)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 5)

    def test_review_must_have_valid_rating(self):
        """Test that a review must have a rating between 1 and 5."""
        review = Review(shop=self.shop, user=self.user, rating=6, comment="Too high")
        with self.assertRaises(ValidationError):
            review.full_clean()

        review.rating = 0  # Too low
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_review_must_have_shop_and_user(self):
        """Test that a review must be linked to a shop and user."""
        review = Review(shop=None, user=self.user, rating=3, comment="No shop linked")
        with self.assertRaises(ValidationError):
            review.full_clean()

        review = Review(shop=self.shop, user=None, rating=3, comment="No user linked")
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_deleting_shop_deletes_reviews(self):
        """Test that deleting a shop also deletes its reviews (CASCADE)"""
        review = Review.objects.create(
            shop=self.shop, user=self.user, rating=4, comment="Great products!"
        )
        self.shop.delete()

        with self.assertRaises(Review.DoesNotExist):  # The review should be gone
            Review.objects.get(id=review.id)

    def test_deleting_user_deletes_reviews(self):
        """Test that deleting a user also deletes their reviews (CASCADE)"""
        review = Review.objects.create(
            shop=self.shop, user=self.user, rating=5, comment="Amazing!"
        )
        self.user.delete()

        with self.assertRaises(Review.DoesNotExist):  # The review should be gone
            Review.objects.get(id=review.id)


class CartItemModelTest(TestCase):
    """Tests for the CartItemModel functionality.

    This test suite verifies the creation, validation, and deletion behavior of the
    CartItem model. It ensures that cart items are properly linked to both carts and
    book listings, validates constraints such as required relationships and positive
    quantities, and checks cascading deletion behavior for associated carts and book listings.

    Test Cases:
    - Successful creation of a cart item linked to a cart and book listing.
    - Validation to ensure cart items are linked to both a cart and a book listing.
    - Validation to ensure cart items have a positive quantity.
    - Cascading deletion of cart items when their associated cart is deleted.
    - Cascading deletion of cart items when their associated book listing is deleted.
    """

    def setUp(self):
        """Create a sample cart and book listing for testing"""
        self.user = User.objects.create(
            email="buyer@example.com", name="Buyer User", role="buyer"
        )
        self.cart = Cart.objects.create(user=self.user)

        self.shop = Shop.objects.create(name="Bookstore", user=self.user)
        self.book_listing = BookListing.objects.create(
            shop=self.shop,
            title="Django for Beginners",
            author="William S. Vincent",
            condition="good",
            price=29.99,
        )

    def test_cart_item_creation(self):
        """Test if a cart item is created successfully."""
        cart_item = CartItem.objects.create(
            cart=self.cart, book_listing=self.book_listing, quantity=2
        )
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.book_listing, self.book_listing)
        self.assertEqual(cart_item.quantity, 2)

    def test_cart_item_must_have_cart_and_book_listing(self):
        """Test that a cart item must be linked to a cart and a book listing."""
        cart_item = CartItem(cart=None, book_listing=self.book_listing, quantity=1)
        with self.assertRaises(ValidationError):
            cart_item.full_clean()

        cart_item = CartItem(cart=self.cart, book_listing=None, quantity=1)
        with self.assertRaises(ValidationError):
            cart_item.full_clean()

    def test_cart_item_must_have_positive_quantity(self):
        """Test that a cart item must have a positive quantity."""
        cart_item = CartItem(
            cart=self.cart, book_listing=self.book_listing, quantity=-1
        )
        with self.assertRaises(ValidationError):
            cart_item.full_clean()

        cart_item.quantity = 0
        with self.assertRaises(ValidationError):
            cart_item.full_clean()

    def test_deleting_cart_deletes_cart_items(self):
        """Test that deleting a cart also deletes its cart items (CASCADE)"""
        cart_item = CartItem.objects.create(
            cart=self.cart, book_listing=self.book_listing, quantity=1
        )
        self.cart.delete()

        with self.assertRaises(CartItem.DoesNotExist):  # The cart item should be gone
            CartItem.objects.get(id=cart_item.id)

    def test_deleting_book_listing_deletes_cart_items(self):
        """Test that deleting a book listing also deletes its cart items (CASCADE)"""
        cart_item = CartItem.objects.create(
            cart=self.cart, book_listing=self.book_listing, quantity=1
        )
        self.book_listing.delete()

        with self.assertRaises(CartItem.DoesNotExist):  # The cart item should be gone
            CartItem.objects.get(id=cart_item.id)


class OrderItemModelTest(TestCase):
    """Tests for the OrderItemModel functionality.

    This test suite validates the creation, constraints, and deletion behavior of the
    OrderItem model. It ensures that order items are properly linked to an order and
    a book listing, enforces constraints such as positive quantities and purchase prices,
    and verifies cascading deletions for related orders and book listings.

    Test Cases:
    - Successful creation of an order item linked to an order and a book listing.
    - Validation to ensure order items are linked to both an order and a book listing.
    - Validation to ensure order items have positive quantities.
    - Validation to ensure order items have positive purchase prices.
    - Verification of cascading deletion of order items when their associated order is deleted.
    - Verification of cascading deletion of order items when their associated book listing is deleted.
    """

    def setUp(self):
        """Create a sample order and book listing for testing"""
        self.user = User.objects.create(
            email="buyer@example.com", name="Buyer User", role="buyer"
        )
        self.order = Order.objects.create(user=self.user, total_price=100.00)

        self.shop = Shop.objects.create(name="Bookstore", user=self.user)
        self.book_listing = BookListing.objects.create(
            shop=self.shop,
            title="Django for Beginners",
            author="William S. Vincent",
            condition="good",
            price=29.99,
        )

    def test_order_item_creation(self):
        """Test if an order item is created successfully."""
        order_item = OrderItem.objects.create(
            order=self.order,
            book_listing=self.book_listing,
            quantity=2,
            purchase_price=29.99,
        )
        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.book_listing, self.book_listing)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.purchase_price, 29.99)

    def test_order_item_must_have_order_and_book_listing(self):
        """Test that an order item must be linked to an order and a book listing."""
        order_item = OrderItem(
            order=None, book_listing=self.book_listing, quantity=1, purchase_price=20.00
        )
        with self.assertRaises(ValidationError):
            order_item.full_clean()

        order_item = OrderItem(
            order=self.order, book_listing=None, quantity=1, purchase_price=20.00
        )
        with self.assertRaises(ValidationError):
            order_item.full_clean()

    def test_order_item_must_have_positive_quantity(self):
        """Test that an order item must have a positive quantity."""
        order_item = OrderItem(
            order=self.order,
            book_listing=self.book_listing,
            quantity=-1,
            purchase_price=20.00,
        )
        with self.assertRaises(ValidationError):
            order_item.full_clean()

        order_item.quantity = 0
        with self.assertRaises(ValidationError):
            order_item.full_clean()

    def test_order_item_must_have_positive_purchase_price(self):
        """Test that an order item must have a positive purchase price."""
        order_item = OrderItem(
            order=self.order,
            book_listing=self.book_listing,
            quantity=1,
            purchase_price=-5.00,
        )
        with self.assertRaises(ValidationError):
            order_item.full_clean()

        order_item.purchase_price = 0
        with self.assertRaises(ValidationError):
            order_item.full_clean()

    def test_deleting_order_deletes_order_items(self):
        """Test that deleting an order also deletes its order items (CASCADE)"""
        order_item = OrderItem.objects.create(
            order=self.order,
            book_listing=self.book_listing,
            quantity=1,
            purchase_price=29.99,
        )
        self.order.delete()

        with self.assertRaises(OrderItem.DoesNotExist):  # The order item should be gone
            OrderItem.objects.get(id=order_item.id)

    def test_deleting_book_listing_deletes_order_items(self):
        """Test that deleting a book listing also deletes its order items (CASCADE)"""
        order_item = OrderItem.objects.create(
            order=self.order,
            book_listing=self.book_listing,
            quantity=1,
            purchase_price=29.99,
        )
        self.book_listing.delete()

        with self.assertRaises(OrderItem.DoesNotExist):  # The order item should be gone
            OrderItem.objects.get(id=order_item.id)


class OrderAssignmentModelTest(TestCase):
    """Tests for the OrderAssignmentModel functionality.

        This test suite validates the creation, constraints, and deletion behavior of the
        OrderAssignment model. It ensures that order assignments are properly linked to
        both an order and a courier, enforces constraints such as uniqueness of assignments
        per order, and verifies cascading deletions of assignments when their related orders
        or couriers are deleted.

    Test Cases:
    - Successful creation of an order assignment linked to an order and a courier.
    - Validation to ensure order assignments are linked to both an order and a courier.
    - Validation to ensure that an order can have only one assignment.
    - Verification of cascading deletion of assignments when their associated order is deleted.
    - Verification of cascading deletion of assignments when their associated courier is deleted.
    """

    def setUp(self):
        """Create a sample order and courier user for testing"""
        self.courier = User.objects.create(
            email="courier@example.com", name="Courier User", role="courier"
        )
        self.user = User.objects.create(
            email="buyer@example.com", name="Buyer User", role="buyer"
        )
        self.order = Order.objects.create(user=self.user, total_price=150.00)

    def test_order_assignment_creation(self):
        """Test if an order assignment is created successfully."""
        assignment = OrderAssignment.objects.create(
            order=self.order, courier=self.courier
        )
        self.assertEqual(assignment.order, self.order)
        self.assertEqual(assignment.courier, self.courier)
        self.assertIsNotNone(assignment.assigned_at)

    def test_order_assignment_must_have_order_and_courier(self):
        """Test that an order assignment must be linked to an order and a courier."""
        assignment = OrderAssignment(order=None, courier=self.courier)
        with self.assertRaises(ValidationError):
            assignment.full_clean()

        assignment = OrderAssignment(order=self.order, courier=None)
        with self.assertRaises(ValidationError):
            assignment.full_clean()

    def test_order_can_have_only_one_assignment(self):
        """Test that an order can have only one assignment."""
        OrderAssignment.objects.create(order=self.order, courier=self.courier)

        with self.assertRaises(ValidationError):
            duplicate_assignment = OrderAssignment(
                order=self.order, courier=self.courier
            )
            duplicate_assignment.full_clean()

    def test_deleting_order_deletes_assignment(self):
        """Test that deleting an order also deletes its assignment (CASCADE)"""
        assignment = OrderAssignment.objects.create(
            order=self.order, courier=self.courier
        )
        self.order.delete()

        with self.assertRaises(
            OrderAssignment.DoesNotExist
        ):  # The assignment should be gone
            OrderAssignment.objects.get(id=assignment.id)

    def test_deleting_courier_deletes_assignment(self):
        """Test that deleting a courier also deletes their assignments (CASCADE)"""
        assignment = OrderAssignment.objects.create(
            order=self.order, courier=self.courier
        )
        self.courier.delete()

        with self.assertRaises(
            OrderAssignment.DoesNotExist
        ):  # The assignment should be gone
            OrderAssignment.objects.get(id=assignment.id)


class DeliveryIssueModelTest(TestCase):
    """Tests for the DeliveryIssueModel functionality.

    This test suite validates the creation, constraints, and deletion behavior of the
    DeliveryIssue model. It ensures that delivery issues are properly linked to
    order assignments, enforce constraints such as mandatory descriptions and assignments,
    and verify cascading deletions of delivery issues when their related order assignments are deleted.

    Test Cases:
    - Successful creation of a delivery issue linked to an order assignment.
    - Validation to ensure delivery issues are linked to an order assignment.
    - Validation to ensure delivery issues have a mandatory description.
    - Validation to ensure order assignments can have only one associated delivery issue.
    - Verification of cascading deletion of a delivery issue when its related order assignment is deleted.
    """

    def setUp(self):
        """Create a sample order, courier user, and order assignment for testing"""
        self.courier = User.objects.create(
            email="courier@example.com", name="Courier User", role="courier"
        )
        self.user = User.objects.create(
            email="buyer@example.com", name="Buyer User", role="buyer"
        )
        self.order = Order.objects.create(user=self.user, total_price=150.00)
        self.assignment = OrderAssignment.objects.create(
            order=self.order, courier=self.courier
        )

    def test_delivery_issue_creation(self):
        """Test if a delivery issue is created successfully."""
        issue = DeliveryIssue.objects.create(
            order_assignment=self.assignment, issue_description="Package was damaged"
        )
        self.assertEqual(issue.order_assignment, self.assignment)
        self.assertEqual(issue.issue_description, "Package was damaged")
        self.assertIsNotNone(issue.reported_at)

    def test_delivery_issue_must_have_order_assignment(self):
        """Test that a delivery issue must be linked to an order assignment."""
        issue = DeliveryIssue(order_assignment=None, issue_description="Package lost")
        with self.assertRaises(ValidationError):
            issue.full_clean()

    def test_delivery_issue_must_have_description(self):
        """Test that a delivery issue must have a description."""
        issue = DeliveryIssue(order_assignment=self.assignment, issue_description="")
        with self.assertRaises(ValidationError):
            issue.full_clean()

    def test_order_assignment_can_have_only_one_issue(self):
        """Test that an order assignment can have only one delivery issue."""
        DeliveryIssue.objects.create(
            order_assignment=self.assignment, issue_description="Delayed delivery"
        )

        with self.assertRaises(ValidationError):
            duplicate_issue = DeliveryIssue(
                order_assignment=self.assignment, issue_description="Another issue"
            )
            duplicate_issue.full_clean()

    def test_deleting_order_assignment_deletes_delivery_issue(self):
        """Test that deleting an order assignment also deletes its issue (CASCADE)"""
        issue = DeliveryIssue.objects.create(
            order_assignment=self.assignment, issue_description="Late delivery"
        )
        self.assignment.delete()

        with self.assertRaises(DeliveryIssue.DoesNotExist):  # The issue should be gone
            DeliveryIssue.objects.get(id=issue.id)
