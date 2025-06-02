from django.db import models
from .review_models import Review


class ReviewWorkImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='masters/reviews_images/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0) 
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order'] 
        
    # def __str__(self):
    #     return f'{self.review.user.full_name} shared images for {self.review.master}'