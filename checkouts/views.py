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
        subject = 'Order Confirmation - Your Order is on the Way!'
        message = f"Hi {order.full_name},\n\nThank you for your order. It has been placed successfully. Your order details are as follows:\n\n"
        
        for product_id, product_info in order.cart_data.items():
            message += f"Product: {product_info['name']}\n"
            message += f"Price: ${product_info['price']}\n"
            message += f"Quantity: {product_info['quantity']}\n"
            message += f"Total: ${product_info['total']}\n\n"

        message += f"Total Order Value: ${order.cart_total}\n\n"
        message += "Your order will be shipped to:\n"
        message += f"Address: {order.shipping_address}\n\n"
        message += "Thank you for shopping with us!\n\nBest regards,\nThe Team"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [order.email])
        request.session['cart'] = {}
        return redirect('home')

    return render(request, 'checkouts/checkout.html', {'cart_total': cart_total})


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