from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(pk=product_id)
        item_total = product.price * quantity
        total += item_total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total': item_total,
        })

    context = {'cart_items': cart_items, 'cart_total': total}
    return render(request, 'carts/cart.html', context)


def add_to_cart_view(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)] += 1  
    else:
        cart[str(product_id)] = 1 

    request.session['cart'] = cart
    return redirect('cart')  


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id] 
        request.session['cart'] = cart

    return redirect('cart') 

@csrf_exempt
def update_cart_quantity(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        data = json.loads(request.body)
        quantity = data.get('quantity', 1)

        if str(product_id) in cart:
            cart[str(product_id)] = quantity
            request.session['cart'] = cart
            cart_total = sum(Product.objects.get(id=int(product_id)).price * qty for product_id, qty in cart.items())

            return JsonResponse({
                'status': 'success',
                'total': cart_total
            })

        return JsonResponse({'status': 'error', 'message': 'Product not found in cart'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
