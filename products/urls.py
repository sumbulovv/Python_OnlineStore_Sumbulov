from django.urls import path
from .views import (
    add_category, 
    add_product, 
    category_list, 
    product_list, 
    product_detail, 
    update_product,
    product_list_by_category
    )

urlpatterns = [
    path('products/', product_list, name='product_list'),
    path('products/category/<int:category_id>/', product_list_by_category, name='product_list_by_category'),
    path('products/add/', add_product, name='add_product'),
    path('products/<int:pk>/', product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', update_product, name='update_product'),
    path('categories/add/', add_category, name='add_category'),
    path('categories/', category_list, name='category_list'),
]
