from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from baskets.models import Basket
from orders.models import Order, OrderItem
from products.models import Category, Product, Stock, product_image_path
from tests.factories import create_product, create_product_with_stock, create_user


class ProductModelTestCase(TestCase):
    def test_product_creation(self):
        category = Category.objects.create(name="Test Category")
        product = Product.objects.create(
            name="Test Product",
            description="This is a test product.",
            price=Decimal("9.99"),
            category=category
        )
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.description, "This is a test product.")
        self.assertEqual(product.price, Decimal("9.99"))
        self.assertEqual(product.category, category)

    def test_category_creation(self):
        category = Category.objects.create(name="Test Category")
        self.assertEqual(category.name, "Test Category")

    def test_stock_creation(self):
        category = Category.objects.create(name="Test Category")
        product = Product.objects.create(
            name="Test Product",
            description="This is a test product.",
            price=Decimal("9.99"),
            category=category
        )
        stock = Stock.objects.create(product=product, quantity=5)
        self.assertEqual(stock.product, product)
        self.assertEqual(stock.quantity, 5)

    def test_product_string_returns_name(self):
        product = create_product(name="Laptop")

        self.assertEqual(str(product), "Laptop")

    def test_category_string_returns_name(self):
        category = Category.objects.create(name="Electronics")

        self.assertEqual(str(category), "Electronics")

    def test_stock_string_contains_product_name_and_quantity(self):
        product, stock = create_product_with_stock(name="Mouse", quantity=12)

        self.assertEqual(str(stock), "Mouse - 12 in stock")

    def test_category_with_products_is_protected_from_delete(self):
        category = Category.objects.create(name="Protected Category")
        create_product(category=category)

        with self.assertRaises(ProtectedError):
            category.delete()

    def test_stock_is_unique_for_product(self):
        product, _stock = create_product_with_stock(quantity=3)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Stock.objects.create(product=product, quantity=10)

    def test_deleting_product_deletes_related_stock(self):
        product, stock = create_product_with_stock(quantity=7)

        product.delete()

        self.assertFalse(Stock.objects.filter(pk=stock.pk).exists())

    def test_product_image_path_keeps_extension_and_uses_hash_name(self):
        path = product_image_path(None, "catalog.photo.jpg")
        directory, filename = path.split("/")
        hash_name, extension = filename.rsplit(".", 1)

        self.assertEqual(directory, "products")
        self.assertEqual(extension, "jpg")
        self.assertEqual(len(hash_name), 64)
        self.assertTrue(all(char in "0123456789abcdef" for char in hash_name))


class BasketModelTestCase(TestCase):
    def test_basket_creation(self):
        user = create_user()
        product = create_product()

        basket = Basket.objects.create(user=user, product=product, quantity=2)

        self.assertEqual(basket.user, user)
        self.assertEqual(basket.product, product)
        self.assertEqual(basket.quantity, 2)

    def test_deleting_user_deletes_basket_items(self):
        user = create_user()
        product = create_product()
        basket = Basket.objects.create(user=user, product=product, quantity=2)

        user.delete()

        self.assertFalse(Basket.objects.filter(pk=basket.pk).exists())

    def test_deleting_product_deletes_basket_items(self):
        user = create_user()
        product = create_product()
        basket = Basket.objects.create(user=user, product=product, quantity=2)

        product.delete()

        self.assertFalse(Basket.objects.filter(pk=basket.pk).exists())

    def test_basket_total_price(self):
        user = create_user()
        product = create_product(price=Decimal("12.50"))
        basket = Basket.objects.create(user=user, product=product, quantity=3)

        self.assertEqual(basket.total_price, Decimal("37.50"))


class OrderModelTestCase(TestCase):
    def test_order_item_keeps_product_snapshot_and_total_price(self):
        user = create_user()
        product = create_product(name="Notebook", price=Decimal("15.00"))
        order = Order.objects.create(user=user, total_price=Decimal("30.00"))
        item = OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            price=product.price,
            quantity=2,
        )

        product.name = "Updated Notebook"
        product.price = Decimal("99.00")
        product.save()
        item.refresh_from_db()

        self.assertEqual(item.product_name, "Notebook")
        self.assertEqual(item.price, Decimal("15.00"))
        self.assertEqual(item.total_price, Decimal("30.00"))
