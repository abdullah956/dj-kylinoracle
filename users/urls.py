from django.urls import path
from .views import (
    hello_view,
    about_view,
    contact_view,
    blog_list_view,
    testimonials_view,
    product_view,
    description_view,
    cart_view,
    checkout_view
)


urlpatterns = [
    path('', hello_view, name='home'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('blog/', blog_list_view, name='blog'),
    path('testimonials/', testimonials_view, name='testimonial'),
    path('products/', product_view, name='products'),
    path('description/', description_view, name='description'),
    path('cart/', cart_view, name='cart'),
    path('checkout/', checkout_view, name='checkout'),
]

