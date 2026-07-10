from django.contrib import admin

from products.models import Category, Product, Stock

# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Stock)