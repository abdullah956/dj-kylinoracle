from django.db import models
from config.models import BasedModel

class Order(BasedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]

    cart_data = models.JSONField()
    cart_total = models.DecimalField(max_digits=10, decimal_places=2)  
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    city = models.CharField(max_length=100)
    shipping_address = models.TextField()
    paypal_payment = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order {self.id} - {self.full_name}"



