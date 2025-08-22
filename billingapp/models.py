from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    def __str__(self):
        return self.username
    
class Company(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company")
  
    name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    tax_number = models.CharField(max_length=100, blank=True, null=True)
    
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    theme_color = models.CharField(max_length=20, default="#000000")  # For theming
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

