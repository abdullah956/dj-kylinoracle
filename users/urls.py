from django.urls import path
from .views import (
    home_view,
    about_view,
    contact_view,
    testimonials_view,
    newsletter_signup,
)


urlpatterns = [
    path('', home_view, name='home'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('testimonials/', testimonials_view, name='testimonial'),
    path('newsletter-signup/', newsletter_signup, name='newsletter_signup'),
]

