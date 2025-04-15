from django.shortcuts import render, redirect
from .models import Order
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import openpyxl
from products.models import Product  
from django.utils.dateparse import parse_date
from .forms import OrderDateFilterForm
from django.views.decorators.csrf import csrf_exempt
import json
import paypalrestsdk

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})


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
    print(cart_total)
    if request.method == 'POST':
        request.session['checkout_data'] = {
            'full_name': request.POST.get('full_name'),
            'phone_number': request.POST.get('phone_number'),
            'email': request.POST.get('email'),
            'city': request.POST.get('city'),
            'shipping_address': request.POST.get('shipping_address'),
        }
        return JsonResponse({'status': 'ok'})
    
    return render(request, 'checkouts/checkout.html', {'cart_total': cart_total,'paypal_client_id': settings.PAYPAL_CLIENT_ID })

@csrf_exempt
def save_order_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart_data = request.session.get('cart', {})

            if not cart_data:
                return JsonResponse({'error': 'Missing cart data'}, status=400)

            cart_total = sum(
                float(get_object_or_404(Product, id=pid).price) * qty
                for pid, qty in cart_data.items()
            )

            order = Order.objects.create(
                cart_data=cart_data,
                full_name=data.get('full_name'),
                phone_number=data.get('phone_number'),
                email=data.get('email'),
                city=data.get('city'),
                shipping_address=data.get('shipping_address'),
                cart_total=cart_total,
                paid=True
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

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


def claim_checkout_view(request):
    if request.method == 'POST':
        claim_data = request.session.get('claim_checkout')
        if not claim_data:
            return redirect('claim')

        order = Order.objects.create(
            full_name=request.POST.get('full_name'),
            phone_number=request.POST.get('phone_number'),
            email=request.POST.get('email'),
            city=request.POST.get('city'),
            shipping_address=request.POST.get('shipping_address'),
            cart_data={'claim': 'Free Claim'},
            cart_total=claim_data.get('price'),
            paypal_payment=True
        )

        subject = 'Free Claim Confirmation - Your Order is Confirmed!'
        message = f"Hi {order.full_name},\n\nThank you for claiming your free product. Your order has been successfully placed.\n\n"
        message += "Order Details:\n"
        message += "Product: Free Claim\n"
        message += f"Total: ${order.cart_total}\n\n"
        message += "Shipping Address:\n"
        message += f"{order.shipping_address}\n\n"
        message += "We hope you enjoy your product!\n\nBest regards,\nThe Team"

        send_mail(subject, message, settings.EMAIL_HOST_USER, [order.email])

        del request.session['claim_checkout']
        return redirect('home')

    elif request.method == 'GET':
        claim_data = request.session.get('claim_checkout')
        if not claim_data:
            return redirect('claim')

        return render(request, 'checkouts/claim_checkout.html', {
            'cart_total': claim_data.get('price')
        })
 

