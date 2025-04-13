from django.db import models
from config.models import BasedModel

class ContactMessage(BasedModel):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.subject}"
    
class NewsletterSubscriber(BasedModel):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email