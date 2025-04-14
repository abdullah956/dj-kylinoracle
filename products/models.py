from django.db import models
from users.models import BasedModel 

class Category(BasedModel):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Product(BasedModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return self.name