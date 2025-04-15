from django.shortcuts import render, redirect
from .forms import ContactMessageForm,NewsletterSubscriberForm
from django.contrib import messages
from products.models import Product, Review
from django.db.models import Count

def home_view(request):
    products = Product.objects.all()
    form = NewsletterSubscriberForm()

    if request.method == 'POST':
        form = NewsletterSubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.path)

    reviews = (
        Review.objects.filter(rating=5)
        .select_related('product')
        .values('product')
        .annotate(count=Count('product'))
        .order_by('-count')[:3]
    )

    product_ids = [r['product'] for r in reviews]
    testimonials = Review.objects.filter(product__in=product_ids, rating=5).select_related('product')[:9]

    return render(request, 'home.html', {
        'products': products,
        'form': form,
        'testimonials': testimonials
    })


def about_view(request):
    return render(request, 'users/about.html')

def contact_view(request):
    form = ContactMessageForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('contact')
    return render(request, 'users/contact.html', {'form': form})

def testimonials_view(request):
    reviews = (
        Review.objects.filter(rating=5)
        .select_related('product')
        .values('product')
        .annotate(count=Count('product'))
        .order_by('-count')[:3]
    )

    product_ids = [r['product'] for r in reviews]

    testimonials = Review.objects.filter(product__in=product_ids, rating=5).select_related('product')[:9]
    return render(request, 'users/testimonial.html', {'testimonials': testimonials})

def newsletter_signup(request):
    if request.method == 'POST':
        form = NewsletterSubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Subscribed successfully!")
        else:
            messages.error(request, "Invalid email. Please try again.")
    return redirect(request.META.get('HTTP_REFERER', '/'))
