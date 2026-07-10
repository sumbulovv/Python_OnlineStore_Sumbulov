from django.test import TestCase

from baskets.forms import BasketForm
from products.forms import CategoryForm, ProductForm
from tests.factories import create_category, create_product


class ProductFormTestCase(TestCase):
    def test_product_form_accepts_valid_data_with_stock(self):
        category = create_category()
        form = ProductForm(
            data={
                "name": "Keyboard",
                "description": "Compact mechanical keyboard",
                "price": "149.90",
                "category": category.pk,
                "stock": 4,
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["stock"], 4)

    def test_product_form_rejects_negative_stock(self):
        category = create_category()
        form = ProductForm(
            data={
                "name": "Keyboard",
                "description": "Compact mechanical keyboard",
                "price": "149.90",
                "category": category.pk,
                "stock": -1,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("stock", form.errors)


class CategoryFormTestCase(TestCase):
    def test_category_form_accepts_name(self):
        form = CategoryForm(data={"name": "Books"})

        self.assertTrue(form.is_valid())

    def test_category_form_rejects_empty_name(self):
        form = CategoryForm(data={"name": ""})

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)


class BasketFormTestCase(TestCase):
    def test_basket_form_accepts_existing_product_and_positive_quantity(self):
        product = create_product()
        form = BasketForm(data={"product": product.pk, "quantity": 2})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["product"], product)
        self.assertEqual(form.cleaned_data["quantity"], 2)

    def test_basket_form_rejects_zero_quantity(self):
        product = create_product()
        form = BasketForm(data={"product": product.pk, "quantity": 0})

        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)
