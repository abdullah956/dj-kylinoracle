from django.shortcuts import render, redirect
from .models import Order
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import openpyxl
from products.models import Product  
from django.utils.dateparse import parse_date
from .forms import OrderDateFilterForm

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

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def checkout_special_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        print(request.POST)
        entered_price = max(float(request.POST.get('price', 50)), 50.00)
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        city = request.POST.get('city')
        shipping_address = request.POST.get('shipping_address')
        if not full_name or not phone_number or not email or not city or not shipping_address:
            print("Missing required billing information")
            return render(request, 'checkouts/special_checkout.html', {
                'product': product,
                'entered_price': entered_price,
                'cart_total': entered_price,
                'error': "Please fill out all required fields."
            })
        Order.objects.create(
            cart_data={ 
                str(product_id): {
                    'name': product.name,
                    'price': entered_price,
                    'quantity': 1,
                    'total': entered_price,
                    'image': product.image.url if product.image else '',
                    'code': product.code if hasattr(product, 'code') else ''
                }
            },
            cart_total=entered_price,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            city=city,
            shipping_address=shipping_address,
            paypal_payment=True
        )
        return redirect('home')
    entered_price = max(float(request.GET.get('price', 50)), 50.00)
    return render(request, 'checkouts/special_checkout.html', {
        'product': product,
        'entered_price': entered_price,
        'cart_total': entered_price
    })


def order_list_view(request):
    form = OrderDateFilterForm(request.GET)
    orders = Order.objects.all().order_by('-created_at')
    
    if form.is_valid():
        filter_date = form.cleaned_data.get('filter_date')
        
        if filter_date:
            orders = orders.filter(created_at__date=filter_date)

    return render(request, 'checkouts/order_list.html', {'orders': orders, 'form': form})

def order_detail_view(request, id):
    order = get_object_or_404(Order, id=id)
    return render(request, 'checkouts/order_detail.html', {'order': order})

def download_orders_excel(request):
    orders = Order.objects.all()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Orders"
    headers = ['Order ID', 'Customer Name', 'Email', 'Total', 'Status', 'Shipping Address', 'Phone']
    ws.append(headers)

    for order in orders:
        row = [
            order.id,
            order.full_name,
            order.email,
            order.cart_total,
            order.get_status_display(),
            order.shipping_address,
            order.phone_number
        ]
        ws.append(row)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=orders.xlsx'
    wb.save(response)
    return response
