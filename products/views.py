from django.shortcuts import redirect, render
from .forms import CategoryForm, ProductForm
from .models import Product, Category, Stock
from django.contrib.auth.decorators import login_required

# Create your views here.
def product_list(request):
    products = Product.objects.select_related('category').all()
    context = {'products': products}
    return render(request, 'product_list.html', context)


def product_detail(request, pk):
    product = Product.objects.select_related('category', 'stock').get(pk=pk)
    stock = product.stock.quantity if hasattr(product, 'stock') else 0
    context = {'product': product, 'stock': stock}
    return render(request, 'product_detail.html', context)


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            Stock.objects.create(product=product, quantity=form.cleaned_data['stock'])
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


@login_required
def update_product(request, pk):
    product = Product.objects.select_related('category', 'stock').get(pk=pk)
    stock = product.stock.quantity if hasattr(product, 'stock') else 0
        
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            quantity = form.cleaned_data['stock']
            if hasattr(product, 'stock'):
                product.stock.quantity = quantity
                product.stock.save()
            else:
                Stock.objects.create(product=product, quantity=quantity)
            return redirect('product_list')
    else:
        form = ProductForm(instance=product, initial={'stock': stock})
    return render(request, 'add_product.html', {'form': form, 'product': product})


def category_list(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'category_list.html', context)


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
        return render(request, 'add_category.html', {
            'form': form,
            'error': 'Название категории не может быть пустым'
        })
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})
