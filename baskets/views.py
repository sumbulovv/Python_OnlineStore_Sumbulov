from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import BasketForm
from .models import Basket

# Create your views here.
@login_required
def add_to_basket(request):
    if request.method == 'POST':
        form = BasketForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            stock = product.stock.quantity if hasattr(product, 'stock') else 0
            if quantity > stock:
                return render(request, 'add_to_basket.html', {
                    'form': form, 
                    'error': 'Недостаточно товара на складе'
                })
                
            basket, created = Basket.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity},
            )
            if not created:
                basket.quantity += quantity
                basket.save()
            if hasattr(product, 'stock'):
                product.stock.quantity -= quantity
                product.stock.save()
            return redirect('view_basket')
    else:
        form = BasketForm()
    return render(request, 'add_to_basket.html', {'form': form})


@login_required
def view_basket(request):
    if request.user.is_authenticated:
        basket_items = Basket.objects.select_related('product').filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in basket_items)
    else:
        basket_items = []
        total_price = 0
    return render(request, 'view_basket.html', {'basket_items': basket_items, 'total_price': total_price})
