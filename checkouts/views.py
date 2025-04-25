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
from openpyxl import Workbook
from datetime import datetime

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
    print(settings.PAYPAL_CLIENT_ID)
    return render(request, 'checkouts/checkout.html', {'cart_total': cart_total,'paypal_client_id': settings.PAYPAL_CLIENT_ID })


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
                    cart_data={"Free Claim": "Free Claim"},
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

    # Filter out orders that contain 'Free Claim'
    normal_orders = [
        order for order in orders
        if not any(value == 'Free Claim' for value in order.cart_data.values())
    ]

    return render(request, 'checkouts/order_list.html', {
        'orders': normal_orders,
        'form': form
    })

def claim_list_view(request):
    form = OrderDateFilterForm(request.GET)
    orders = Order.objects.all().order_by('-created_at')

    if form.is_valid():
        filter_date = form.cleaned_data.get('filter_date')
        if filter_date:
            orders = orders.filter(created_at__date=filter_date)

    # Only include orders that contain 'Free Claim'
    claim_orders = [
        order for order in orders
        if any(value == 'Free Claim' for value in order.cart_data.values())
    ]

    return render(request, 'checkouts/claim_list.html', {
        'orders': claim_orders,
        'form': form
    })


def order_detail_view(request, id):
    order = get_object_or_404(Order, id=id)
    cart_items = []

    for product_id, product_info in order.cart_data.items():
        if isinstance(product_info, str) and product_info == 'Free Claim':
            cart_items.append({
                'name': 'Claim',
                'price': order.cart_total, 
                'quantity': 1,
                'total': order.cart_total,
                'image': None
            })

        elif isinstance(product_info, dict): 
            try:
                product = Product.objects.get(id=product_id)
                image_url = product.image.url if product.image else None
            except Product.DoesNotExist:
                image_url = None

            cart_items.append({
                'name': product_info.get('name', 'Unknown Product'),
                'price': product_info.get('price', 0),
                'quantity': product_info.get('quantity', 1),
                'total': product_info.get('price', 0) * product_info.get('quantity', 1),
                'image': image_url
            })

        else:
            try:
                product = Product.objects.get(id=product_id)  
                cart_items.append({
                    'name': product.name,
                    'price': product.price,
                    'quantity': product_info,  
                    'total': product.price * product_info,
                    'image': product.image.url if product.image else None
                })
            except Product.DoesNotExist:
                cart_items.append({
                    'name': 'Unknown Product',
                    'price': 0,
                    'quantity': product_info,
                    'total': 0,
                    'image': None
                })

    return render(request, 'checkouts/order_detail.html', {
        'order': order,
        'cart_items': cart_items
    })



def download_orders_excel(request):
    filter_date = request.GET.get('filter_date')
    orders = Order.objects.all()
    if filter_date:
        try:
            filter_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date=filter_date)
        except ValueError:
            orders = orders
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"
    headers = ['Order ID', 'Customer Name', 'Email', 'Total', 'Status', 'Shipping Address', 'Phone', 'Paid']
    ws.append(headers)
    for order in orders:
        row = [
            order.id,
            order.full_name,
            order.email,
            order.cart_total,
            order.get_status_display(),
            order.shipping_address,
            order.phone_number,
            order.paid 
        ]
        ws.append(row)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=orders.xlsx'
    wb.save(response)
    return response

def update_order_status(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            if new_status in ['shipped', 'delivered']:
                send_mail(
                    f"Your order #{order.id} has been {new_status}",
                    f"Hi {order.full_name}, your order has been {new_status}. Thank you!",
                    settings.DEFAULT_FROM_EMAIL,
                    [order.email],
                    fail_silently=True,
                )
    return redirect(request.META.get('HTTP_REFERER', '/'))