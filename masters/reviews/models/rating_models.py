from django.db import models
from django.db.models import Avg, Count
from django.core.validators import MinValueValidator, MaxValueValidator
from .comment_models import User


class Rating(models.Model):
    master = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings') 
    user = models.CharField(max_length=255)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])  
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('master', 'user')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        master_rating, created = MasterRating.objects.get_or_create(master=self.master)
        master_rating.update()


class MasterRating(models.Model):
    master = models.OneToOneField(User, on_delete=models.CASCADE, related_name='master_rating')
    average_rating = models.FloatField(default=0)
    rating_count = models.PositiveIntegerField(default=0)

    def update(self):
        agg = self.master.ratings.aggregate(avg=Avg('rating'), count=Count('id'))
        self.average_rating = agg['avg'] or 0
        self.rating_count = agg['count']
        self.save()