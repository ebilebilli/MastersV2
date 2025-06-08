from django.db import models
from .master_model import CustomerUser


class MasterWorkImage(models.Model):
    master = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='masters/master_handwork_images/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0) 
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order'] 
        
    def __str__(self):
        return f'Image for {self.master.full_name}'