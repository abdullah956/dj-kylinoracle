from django.urls import path
from .views import (
    checkout_view,checkout_special_view
)

urlpatterns = [
    path('checkout/', checkout_view, name='checkout'),
    path('special-checkout/<int:product_id>/', checkout_special_view, name='special_checkout'),
]

