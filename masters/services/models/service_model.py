from django.db import models
from django.contrib.auth import get_user_model

from .category_model import Category
from core.models.city_model import City


User = get_user_model()

class ServiceTemplate(models.Model):
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='service_templates'
        )
    name = models.CharField(max_length=100)  
    display_name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name} ({self.category.display_name})'



