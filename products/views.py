from django.shortcuts import render
from .models import Category , Product

def product_view(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    return render(request, 'products/product.html', {'categories': categories, 'products': products})

def description_view(request, id):
    product = Product.objects.get(id=id)
    return render(request, 'products/description.html', {'product': product})

def nullprice_view(request):
    return render(request, 'products/nullprice.html')