from django.db import models


class Language(models.Model):
    name = models.CharField(
        max_length=20,
        unique=True
        )  
    display_name = models.CharField(
        max_length=20
        ) 

    def __str__(self):
        return self.display_name
