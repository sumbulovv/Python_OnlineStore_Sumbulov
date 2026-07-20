from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from baskets.models import Basket
from orders.models import Order
from tests.factories import create_product_with_stock, create_user


class CheckoutViewTestCase(TestCase):
    def setUp(self):
        self.user = create_user()
        self.product, self.stock = create_product_with_stock(
            name="Desk Lamp",
            price=Decimal("25.50"),
            quantity=3,
        )

    def test_login_required_for_checkout(self):
        response = self.client.get(reverse("checkout"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_checkout_creates_order_from_basket_and_clears_basket(self):
        Basket.objects.create(user=self.user, product=self.product, quantity=2)
        self.client.force_login(self.user)

        response = self.client.post(reverse("checkout"))

        self.assertRedirects(response, reverse("order_history"))
        order = Order.objects.get(user=self.user)
        item = order.items.get()
        self.assertEqual(order.total_price, Decimal("51.00"))
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.product_name, "Desk Lamp")
        self.assertEqual(item.price, Decimal("25.50"))
        self.assertEqual(item.quantity, 2)
        self.assertFalse(Basket.objects.filter(user=self.user).exists())

    def test_checkout_does_not_create_order_from_empty_basket(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("checkout"))

        self.assertRedirects(response, reverse("view_basket"))
        self.assertFalse(Order.objects.filter(user=self.user).exists())

    def test_view_basket_posts_checkout_form(self):
        Basket.objects.create(user=self.user, product=self.product, quantity=2)
        self.client.force_login(self.user)

        response = self.client.get(reverse("view_basket"))

        self.assertContains(response, f'action="{reverse("checkout")}"')
        self.assertContains(response, 'method="post"')
        self.assertContains(response, "Оформить заказ")


class OrderHistoryViewTestCase(TestCase):
    def test_order_history_shows_only_current_user_orders(self):
        user = create_user()
        other_user = create_user(username="otheruser")
        product, _stock = create_product_with_stock(
            name="Keyboard",
            price=Decimal("10.00"),
        )
        other_product, _other_stock = create_product_with_stock(
            name="Mouse",
            price=Decimal("20.00"),
        )
        Basket.objects.create(user=user, product=product, quantity=1)
        Basket.objects.create(user=other_user, product=other_product, quantity=1)
        self.client.force_login(user)
        self.client.post(reverse("checkout"))

        self.client.force_login(other_user)
        self.client.post(reverse("checkout"))

        self.client.force_login(user)
        response = self.client.get(reverse("order_history"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["orders"],
            [product],
            transform=lambda order: order.items.get().product,
        )
