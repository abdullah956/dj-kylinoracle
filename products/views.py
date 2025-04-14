from django.shortcuts import render, get_object_or_404, redirect
from .models import Category , Product, Review
from django.db import models
from .forms import ReviewForm
from django.db.models import Avg


def product_view(request):
    categories = Category.objects.all()
    category_id = request.GET.get('category')

    if category_id and category_id != 'all':
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()

    return render(request, 'products/product.html', {
        'categories': categories,
        'products': products
    })


def description_view(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.save()
            return redirect('description', id=product.id)

    reviews = Review.objects.filter(product=product)
    avg_rating = round(reviews.aggregate(Avg('rating'))['rating__avg'] if reviews.exists() else 0)
    form = ReviewForm()
    filled_stars = range(avg_rating)
    unfilled_stars = range(5 - avg_rating)

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'form': form,
        'filled_stars': filled_stars,
        'unfilled_stars': unfilled_stars
    }

    if product.price is None:
        return render(request, 'products/nullprice.html', context)

    return render(request, 'products/description.html', context)
