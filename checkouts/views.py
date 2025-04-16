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
    request.session.pop('claim_checkout', None) 
    cart_data = request.session.get('cart', {}) 
    if not isinstance(cart_data, dict):
        return HttpResponse("Invalid cart data", status=400)
    if not cart_data: 
        return redirect('cart')  
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
            email = data.get('email')
            full_name = data.get('full_name')
            cart_data = request.session.get('cart', {})
            claim_data = request.session.get('claim_checkout')

            def send_plain_email(subject, message, recipient):
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient],
                    fail_silently=True
                )

            if claim_data and 'price' in claim_data:
                claim_price = float(claim_data['price'])

                order = Order.objects.create(
                    cart_data=claim_data,
                    full_name=full_name,
                    phone_number=data.get('phone_number'),
                    email=email,
                    city=data.get('city'),
                    shipping_address=data.get('shipping_address'),
                    cart_total=claim_price,
                    paid=True
                )

                body = f"Hi {full_name},\n\nYour order has been placed.\n\n"
                body += "Free Claim Item:\n"
                body += f"\nTotal: ${claim_price:.2f}\n\nThank you for your purchase!"
                send_plain_email("Order Confirmation", body, email)

                request.session.pop('claim_checkout', None)
                request.session.pop('cart', None)
                return JsonResponse({'status': 'ok'})

            if cart_data:
                items_text = ""
                cart_total = 0
                for pid, qty in cart_data.items():
                    product = get_object_or_404(Product, id=pid)
                    price = float(product.price)
                    total = price * qty
                    cart_total += total
                    items_text += f"{product.name} - ${price:.2f} x {qty} = ${total:.2f}\n"

                order = Order.objects.create(
                    cart_data=cart_data,
                    full_name=full_name,
                    phone_number=data.get('phone_number'),
                    email=email,
                    city=data.get('city'),
                    shipping_address=data.get('shipping_address'),
                    cart_total=cart_total,
                    paid=True
                )

                body = f"Hi {full_name},\n\nYour order has been placed.\n\n"
                body += "Items:\n" + items_text
                body += f"\nTotal: ${cart_total:.2f}\n\nThank you for your purchase!"
                send_plain_email("Order Confirmation", body, email)

                request.session.pop('cart', None)
                request.session.pop('claim_checkout', None)
                return JsonResponse({'status': 'ok'})

            return JsonResponse({'error': 'No cart or claim data available'}, status=400)

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
    request.session.pop('cart_data', None) 
    claim_data = request.session.get('claim_checkout') 
    if not isinstance(claim_data, dict) or 'price' not in claim_data:
        return HttpResponse("Invalid claim data", status=400)
    cart_total = float(claim_data['price'])

    if request.method == 'POST':
        request.session['checkout_data'] = {
            'full_name': request.POST.get('full_name'),
            'phone_number': request.POST.get('phone_number'),
            'email': request.POST.get('email'),
            'city': request.POST.get('city'),
            'shipping_address': request.POST.get('shipping_address'),
        }
        return JsonResponse({'status': 'ok'})
    return render(request, 'checkouts/checkout.html', {
        'cart_total': cart_total,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID     })
