from django.db import models
from django.contrib.auth.models import AbstractUser

from core.models.city_model import City, District
from core.models.education_model import Education
from core.models.language_model import Language
from services.models.category_model import Category
from services.models.service_model import ServiceTemplate
from masters.utils.validators import phone_validator, az_letters_validator
from utils.constants import GENDER_STATUS


class Master(AbstractUser):
    profession_category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='category_masters'
        )
    profession_service = models.ForeignKey(
        ServiceTemplate,
        on_delete=models.CASCADE,
        related_name='profession_masters'
        )
    custom_profession = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        validators=[az_letters_validator]
        )
    cities = models.ManyToManyField(
        City, 
        related_name='city_masters',
        verbose_name='Şəhərlər'
        )  
    districts = models.ManyToManyField(
        District, 
        related_name='district_masters', 
        blank=True
        )
    education = models.ForeignKey(
        Education,
        related_name='education_masters'
        )
    education_detail = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        validators=[az_letters_validator]
        )
    languages = models.ManyToManyField(
        Language,
        related_name='language_masters',
        verbose_name='Dillər'
        )
    
    full_name = models.CharField(
        max_length=20, 
        validators=[az_letters_validator],
        verbose_name='Ad və soyad'
        )
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    birthday = models.DateField()
    phone_number = models.CharField(
        validators=[phone_validator],
        verbose_name='Mobil nömrə',
        max_length=13
    )
    gender = models.CharField(
        max_length=5, 
        choices=GENDER_STATUS, 
        verbose_name='Cinsiyyət'
        )
    experience = models.PositiveSmallIntegerField()
  
    