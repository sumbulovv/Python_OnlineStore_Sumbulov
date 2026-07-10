from django.urls import path
from .views import add_to_basket, view_basket

urlpatterns = [
    path('add_to_basket/', add_to_basket, name='add_to_basket'),
    path('view_basket/', view_basket, name='view_basket'),
]
