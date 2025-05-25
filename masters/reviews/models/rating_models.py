from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Rating(models.Model):
    master = models.ForeignKey('users.Master', on_delete=models.CASCADE, related_name='ratings') 
    user = models.CharField(max_length=255)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])  
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('master', 'user')

