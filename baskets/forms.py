from django import forms
from products.models import Product
from .models import Basket

class BasketForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), label='Товар')
    quantity = forms.IntegerField(min_value=1, label='Количество')
    
    
