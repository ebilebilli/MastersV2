from django.db import models


class Language(models.Model):
    name = models.CharField(
        max_length=10,
        unique=True
        )  
    display_name = models.CharField(
        max_length=10
        ) 

    def __str__(self):
        return self.display_name
