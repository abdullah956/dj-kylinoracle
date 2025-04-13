from django.shortcuts import render, redirect
from .models import Order
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


def checkout_view(request):
    # Get cart data from the session
    cart_data = request.session.get('cart', {})

    # Debugging: Print cart data
    print(cart_data)  # Check the content of cart_data

    # Ensure cart_data is a dictionary and contains the correct structure
    if not isinstance(cart_data, dict):
        return HttpResponse("Invalid cart data", status=400)  # Handle invalid cart data

    # Calculate the total
    cart_total = sum(item['price'] * item['quantity'] for item in cart_data.values())  # Calculate total

    # Handle the rest of the checkout logic (handling POST request, etc.)
    if request.method == 'POST':
        # Process order (billing details, etc.)
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        city = request.POST.get('city')
        shipping_address = request.POST.get('shipping_address')
        payment_method = request.POST.get('paymentMethod')

        # Create the order object
        order = Order.objects.create(
            cart_data=cart_data,
            cart_total=cart_total,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            city=city,
            shipping_address=shipping_address,
            payment_method=payment_method
        )

        # Clear the cart after successful order
        request.session['cart'] = {}

        return redirect('home')  # Redirect to a success page

    # If GET request, just render the checkout page with cart data
    return render(request, 'checkouts/checkout.html', {'cart_total': cart_total})
