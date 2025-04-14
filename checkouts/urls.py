from django.urls import path
from .views import (
    checkout_view,checkout_special_view,order_list_view,order_detail_view,download_orders_excel
)

urlpatterns = [
    path('checkout/', checkout_view, name='checkout'),
    path('special-checkout/<int:product_id>/', checkout_special_view, name='special_checkout'),
    path('orders/', order_list_view, name='order_list'),
    path('order/<int:id>/', order_detail_view, name='order_detail'),
    path('orders/download/', download_orders_excel, name='download_orders_excel'), 
]

