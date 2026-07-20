from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from baskets.models import Basket
from orders.models import Order, OrderItem


@login_required
def checkout(request):
    basket_items = (
        Basket.objects.select_related('product')
        .filter(user=request.user)
        .order_by('product__name')
    )
    total_price = sum(item.product.price * item.quantity for item in basket_items)

    if request.method == 'POST':
        if not basket_items.exists():
            messages.warning(request, 'Корзина пуста, заказ не создан.')
            return redirect('view_basket')

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
            )
            OrderItem.objects.bulk_create(
                [
                    OrderItem(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        price=item.product.price,
                        quantity=item.quantity,
                    )
                    for item in basket_items
                ]
            )
            basket_items.delete()

        messages.success(request, f'Заказ #{order.pk} успешно оформлен.')
        return redirect('order_history')

    return render(
        request,
        'checkout.html',
        {'basket_items': basket_items, 'total_price': total_price},
    )


@login_required
def order_history(request):
    orders = (
        Order.objects.prefetch_related('items')
        .filter(user=request.user)
        .order_by('-created_at')
    )
    return render(request, 'order_history.html', {'orders': orders})
