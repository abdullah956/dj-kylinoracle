from django.shortcuts import render

def product_view(request):
    return render(request, 'products/product.html')

def description_view(request):
    return render(request, 'products/description.html')

def nullprice_view(request):
    return render(request, 'products/nullprice.html')