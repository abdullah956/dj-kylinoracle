from django.shortcuts import render


def home_view(request):
    return render(request, 'home.html')

def about_view(request):
    return render(request, 'users/about.html')

def contact_view(request):
    return render(request, 'users/contact.html')

def testimonials_view(request):
    return render(request, 'users/testimonial.html')