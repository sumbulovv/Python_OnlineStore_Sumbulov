from django import forms
from .models import Category, Product


class ProductForm(forms.ModelForm):
    stock = forms.IntegerField(min_value=0, initial=0, label='Количество на складе')

    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'image', 'category')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)