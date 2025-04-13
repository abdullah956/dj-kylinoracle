from django.contrib import admin
from .models import ContactMessage , NewsletterSubscriber

admin.site.register(ContactMessage)
admin.site.register(NewsletterSubscriber)