from django.urls import path
from .views import (
    checkout_view,order_list_view,order_detail_view,download_orders_excel,claim_checkout_view,save_order_view
)

urlpatterns = [
    path('checkout/', checkout_view, name='checkout'),
    path('claim_checkout/', claim_checkout_view, name='claim_checkout'),
    path('orders/', order_list_view, name='order_list'),
    path('order/<int:id>/', order_detail_view, name='order_detail'),
    path('orders/download/', download_orders_excel, name='download_orders_excel'), 
    path('save-order/', save_order_view, name='save_order'),
]

