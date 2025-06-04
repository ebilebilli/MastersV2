from django.db import models

from .category_model import Category
from django.contrib.auth import get_user_model


User = get_user_model()

class Service(models.Model):
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='services'
        )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='custom_services'
    )
    
    name = models.CharField(max_length=100)  
    display_name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name} ({self.category.display_name})'