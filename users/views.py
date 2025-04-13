from django.shortcuts import render, redirect
from .forms import ContactMessageForm,NewsletterSubscriberForm
from django.contrib import messages

def home_view(request):
    return render(request, 'home.html')

def about_view(request):
    return render(request, 'users/about.html')

def contact_view(request):
    form = ContactMessageForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('contact')
    return render(request, 'users/contact.html', {'form': form})

def testimonials_view(request):
    return render(request, 'users/testimonial.html')

def newsletter_signup(request):
    if request.method == 'POST':
        form = NewsletterSubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Subscribed successfully!")
        else:
            messages.error(request, "Invalid email. Please try again.")
    return redirect(request.META.get('HTTP_REFERER', '/'))
