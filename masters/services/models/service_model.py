from django.db import models

from .category_model import Category


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