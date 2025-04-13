from django.urls import path
from .views import (
    cart_view, add_to_cart_view , remove_from_cart, update_cart_quantity
)

urlpatterns = [
    path('', cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', add_to_cart_view, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('update-quantity/<int:product_id>/', update_cart_quantity, name='update_cart_quantity'),
]
