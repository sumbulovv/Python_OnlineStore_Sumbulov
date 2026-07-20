from django.urls import path

from orders.views import checkout, order_history


urlpatterns = [
    path('orders/checkout/', checkout, name='checkout'),
    path('orders/history/', order_history, name='order_history'),
]
