from django.shortcuts import render, redirect
from .models import Order
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from products.models import Product  

def checkout_view(request):
    cart_data = request.session.get('cart', {}) 
    if not isinstance(cart_data, dict):
        return HttpResponse("Invalid cart data", status=400)

    detailed_cart = {}
    cart_total = 0

    for product_id, quantity in cart_data.items():
        product = get_object_or_404(Product, id=product_id)
        total = float(product.price) * quantity
        cart_total += total
        detailed_cart[product_id] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': quantity,
            'total': total,
            'image': product.image.url if product.image else '',
            'code': product.code if hasattr(product, 'code') else ''
        }

    if request.method == 'POST':
        order = Order.objects.create(
        cart_data=detailed_cart,
        cart_total=cart_total,
        full_name=request.POST.get('full_name'),
        phone_number=request.POST.get('phone_number'),
        email=request.POST.get('email'),
        city=request.POST.get('city'),
        shipping_address=request.POST.get('shipping_address'),
        paypal_payment=True
        )

        request.session['cart'] = {}
        return redirect('home')

    return render(request, 'checkouts/checkout.html', {'cart_total': cart_total})
