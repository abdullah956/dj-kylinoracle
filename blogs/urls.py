from django.urls import path
from .views import (
    blog_list_view,
)

urlpatterns = [
    path('blog/', blog_list_view, name='blog'),
]

