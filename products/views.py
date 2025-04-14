from django.shortcuts import render
from .models import Category , Product

def product_view(request):
    categories = Category.objects.all()
    category_id = request.GET.get('category')

    if category_id and category_id != 'all':
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()

    return render(request, 'products/product.html', {
        'categories': categories,
        'products': products
    })

def description_view(request, id):
    product = Product.objects.get(id=id)

    if product.price is None:
        return render(request, 'products/nullprice.html', {'product': product})

    return render(request, 'products/description.html', {'product': product})


def nullprice_view(request):
    return render(request, 'products/nullprice.html')