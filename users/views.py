from django.shortcuts import render

def hello_view(request):
    return render(request, 'index.html')

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')

def blog_list_view(request):
    return render(request, 'blog_list.html')

def testimonials_view(request):
    return render(request, 'testimonial.html')

def product_view(request):
    return render(request, 'product.html')

def description_view(request):
    return render(request, 'description.html')

def cart_view(request):
    return render(request, 'cart.html')

def checkout_view(request):
    return render(request, 'checkout.html')

def price_view(request):
    return render(request, 'nullprice.html')