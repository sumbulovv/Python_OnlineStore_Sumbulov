from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from baskets.models import Basket
from tests.factories import create_product_with_stock, create_user


class AddToBasketViewTestCase(TestCase):
    def setUp(self):
        self.user = create_user()
        self.product, self.stock = create_product_with_stock(
            name="Desk Lamp",
            price=Decimal("25.50"),
            quantity=5,
        )

    def test_login_required_for_add_to_basket(self):
        response = self.client.get(reverse("add_to_basket"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_add_to_basket_creates_item_and_decreases_stock(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("add_to_basket"),
            {"product": self.product.pk, "quantity": 2},
        )

        self.assertRedirects(response, reverse("view_basket"))
        basket = Basket.objects.get(user=self.user, product=self.product)
        self.stock.refresh_from_db()
        self.assertEqual(basket.quantity, 2)
        self.assertEqual(self.stock.quantity, 3)

    def test_add_to_existing_basket_increases_quantity_and_decreases_stock(self):
        Basket.objects.create(user=self.user, product=self.product, quantity=1)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("add_to_basket"),
            {"product": self.product.pk, "quantity": 3},
        )

        self.assertRedirects(response, reverse("view_basket"))
        basket = Basket.objects.get(user=self.user, product=self.product)
        self.stock.refresh_from_db()
        self.assertEqual(basket.quantity, 4)
        self.assertEqual(self.stock.quantity, 2)

    def test_add_to_basket_does_not_create_item_when_stock_is_insufficient(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("add_to_basket"),
            {"product": self.product.pk, "quantity": 6},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Недостаточно товара на складе")
        self.assertFalse(
            Basket.objects.filter(user=self.user, product=self.product).exists()
        )
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 5)


class ViewBasketTestCase(TestCase):
    def test_view_basket_shows_current_user_items_and_total_price(self):
        user = create_user()
        other_user = create_user(username="otheruser")
        product, _stock = create_product_with_stock(price=Decimal("10.50"))
        other_product, _other_stock = create_product_with_stock(
            name="Other Product",
            price=Decimal("99.00"),
        )
        Basket.objects.create(user=user, product=product, quantity=3)
        Basket.objects.create(user=other_user, product=other_product, quantity=1)
        self.client.force_login(user)

        response = self.client.get(reverse("view_basket"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["basket_items"],
            [product],
            transform=lambda item: item.product,
        )
        self.assertEqual(response.context["total_price"], Decimal("31.50"))
