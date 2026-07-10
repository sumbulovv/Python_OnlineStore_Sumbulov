from decimal import Decimal

from django.contrib.auth import get_user_model

from products.models import Category, Product, Stock


def create_category(name="Test Category"):
    return Category.objects.create(name=name)


def create_product(
    *,
    name="Test Product",
    description="This is a test product.",
    price=Decimal("9.99"),
    category=None,
):
    return Product.objects.create(
        name=name,
        description=description,
        price=price,
        category=category or create_category(),
    )


def create_product_with_stock(*, quantity=5, **product_kwargs):
    product = create_product(**product_kwargs)
    stock = Stock.objects.create(product=product, quantity=quantity)
    return product, stock


def create_user(username="testuser", password="testpass123"):
    return get_user_model().objects.create_user(
        username=username,
        password=password,
    )
