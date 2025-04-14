from django.db import models
from users.models import BasedModel 

class Category(BasedModel):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Product(BasedModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Review(BasedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=100)
    reviewer_email = models.EmailField()
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    message = models.TextField()

    def __str__(self):
        return f'Review for {self.product.name} by {self.reviewer_name}'