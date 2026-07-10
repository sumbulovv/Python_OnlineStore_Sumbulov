from django.test import TestCase
from products.models import Product, Category, Stock

class ProductModelTestCase(TestCase):
    def test_product_creation(self):
        category = Category.objects.create(name="Test Category")
        product = Product.objects.create(
            name="Test Product",
            description="This is a test product.",
            price=9.99,
            category=category
        )
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.description, "This is a test product.")
        self.assertEqual(product.price, 9.99)
        self.assertEqual(product.category, category)

    def test_category_creation(self):
        category = Category.objects.create(name="Test Category")
        self.assertEqual(category.name, "Test Category")

    def test_stock_creation(self):
        category = Category.objects.create(name="Test Category")
        product = Product.objects.create(
            name="Test Product",
            description="This is a test product.",
            price=9.99,
            category=category
        )
        stock = Stock.objects.create(product=product, quantity=5)
        self.assertEqual(stock.product, product)
        self.assertEqual(stock.quantity, 5)