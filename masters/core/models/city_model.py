from django.db import models


class City(models.Model):
    name = models.CharField(
        max_length=60,
        unique=True
        )  
    display_name = models.CharField(
        max_length=60
        ) 

    def __str__(self):
        return self.display_name


class District(models.Model):
    city = models.ForeignKey(
        City, 
        on_delete=models.CASCADE, 
        related_name='districts',
        null=True, 
        blank=True
        )
    name = models.CharField(
        max_length=60,
        unique=True
        )  
    display_name = models.CharField(
        max_length=60,
        unique=True
        )
    
    def __str__(self):
        return self.display_name