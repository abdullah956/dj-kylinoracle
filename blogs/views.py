from django.shortcuts import render
from .models import Blog

def blog_list_view(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blogs/blog_list.html', {'blogs': blogs})
