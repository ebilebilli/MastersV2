from django.db import models
from django.core.validators import(
    MinValueValidator, 
    MaxValueValidator, 
    MaxLengthValidator, 
    MinLengthValidator
    )
from django.core.exceptions import ValidationError

from utils.validators import az_letters_validator, not_only_whitespace


class Review(models.Model):
    master = models.ForeignKey('users.CustomerUser', on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey('users.CustomerUser', on_delete=models.SET_NULL, related_name='comments', null=True)
    username = models.CharField(
        max_length=20,
        validators=[az_letters_validator],
        default='Anonim hesab'
        )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1),MaxValueValidator(5)]
    )
    comment = models.TextField(
        max_length=1000,
        validators=[
            az_letters_validator, 
            not_only_whitespace,
            MinLengthValidator(3),
            MaxLengthValidator(1000),
        ]
    )
    responsible = models.PositiveSmallIntegerField(
        verbose_name="Məsuliyyətli",
        validators=[MinValueValidator(1),MaxValueValidator(5)],
        null=True,
        blank=True
    )
    neat = models.PositiveSmallIntegerField(
        verbose_name="Səliqəli",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    time_management = models.PositiveSmallIntegerField(
        verbose_name="Vaxta nəzarət",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    communicative = models.PositiveSmallIntegerField(
        verbose_name="Ünsiyyətcil",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    punctual = models.PositiveSmallIntegerField(
        verbose_name="Dəqiq",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    professional = models.PositiveSmallIntegerField(
        verbose_name="Peşəkar",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    experienced = models.PositiveSmallIntegerField(
        verbose_name="Təcrübəli",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    efficient = models.PositiveSmallIntegerField(
        verbose_name="Səmərəli",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    agile = models.PositiveSmallIntegerField(
        verbose_name="Çevik",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    patient = models.PositiveSmallIntegerField(
        verbose_name="Səbirli",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('master', 'customer')

    def clean(self):
        if self.master and self.master.user_role != 'Master':
            raise ValidationError({'master': 'Seçilmiş istifadəçi usta olmalıdır.'})
        if self.customer and self.customer.user_role != 'Customer':
            raise ValidationError({'user': 'Seçilmiş istifadəçi müştəri olmalıdır.'})
    
    def create(self, validated_data):
        review = Review(**validated_data)
        review.full_clean()  
        review.save()
        return review
   
    def __str__(self):
        return f'{self.customer} wrote review to {self.master}'
