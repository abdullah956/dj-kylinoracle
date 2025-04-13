from django.urls import path
from .views import (
    product_view,
    description_view,
    nullprice_view
)


urlpatterns = [
    path('products/', product_view, name='products'),
    path('product/<int:id>/', description_view, name='description'),
    path('nullprice/', nullprice_view, name='nullprice'),
]

