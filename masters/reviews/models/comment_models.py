from django.db import models
from django.contrib.auth import get_user_model

from services.models.service_model import Service

User = get_user_model()

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    service = models.ForeignKey(Service, related_name='comments')
    
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.text[:50]