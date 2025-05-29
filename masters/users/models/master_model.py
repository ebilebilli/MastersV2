from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.db.models import Avg

from .master_user_manager_model import MasterUserManager
from reviews.models.rating_models import Rating
from core.models.city_model import City, District
from core.models.education_model import Education
from core.models.language_model import Language
from services.models.category_model import Category
from services.models.service_model import Service
from utils.validators import *
from utils.constants import GENDER_STATUS


class Master(AbstractUser):
    username = None
    first_name = None
    last_name = None
    email = None
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']
    objects = MasterUserManager()

    profession_category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='category_masters',
        null=True
    )
    profession_service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='profession_masters',
        null=True
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
        verbose_name='Şəhərlər',
    )
    districts = models.ManyToManyField(
        District,
        related_name='district_masters',
        blank=True,
    )
    education = models.ForeignKey(
        Education,
        on_delete=models.CASCADE,
        related_name='education_masters',
        null=True
    )
    education_detail = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        validators=[az_letters_validator],
    )
    languages = models.ManyToManyField(
        Language,
        related_name='language_masters',
        verbose_name='Dillər',
    )
    full_name = models.CharField(
        max_length=50,
        validators=[validate_full_name],
        verbose_name='Ad və soyad',
        null=True
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )
    birthday = models.DateField(
        validators=[validate_birthday],
        null=True
    )
    phone_number = models.CharField(
        max_length=13,
        validators=[phone_validator],
        verbose_name='Mobil nömrə',
        unique=True,
        null=True
    )
    gender = models.CharField(
        max_length=5,
        choices=GENDER_STATUS,
        verbose_name='Cinsiyyət',
        null=True
    )
    is_active_on_main_page = models.BooleanField(default=False)
    note = models.CharField(
        max_length=1500,
        verbose_name='Qeyd',
        null=True
    )
    experience = models.PositiveSmallIntegerField(
        null=True,
    )
    facebook_url = models.URLField(
        blank=True,
        null=True,
        validators=[SocialURLValidator.facebook]
    )
    instagram_url = models.URLField(
        blank=True,
        null=True,
        validators=[SocialURLValidator.instagram]
    )
    tiktok_url = models.URLField(
        blank=True,
        null=True,
        validators=[SocialURLValidator.tiktok]
    )
    linkedin_url = models.URLField(
        blank=True,
        null=True,
        validators=[SocialURLValidator.linkedin]
    )
    youtube_url = models.URLField(
        blank=True,
        null=True,
        validators=[SocialURLValidator.youtube]
    )
    slug = models.SlugField(
        unique=True, 
        blank=True, 
        editable=False
    )
    latitude = models.FloatField(
        null=True, 
        blank=True
    )
    longitude = models.FloatField(
        null=True, 
        blank=True
    )
    @property
    def average_rating(self):
        return Rating.objects.filter(master=self).aggregate(avg=Avg('rating'))['avg'] or 0

    @property
    def rating_count(self):
        return Rating.objects.filter(master=self).count()
    
    def save(self, *args, **kwargs):
        if not self.slug and self.full_name:
            base_slug = slugify(self.full_name)
            unique_slug = base_slug
            i = 1
            while Master.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{base_slug}-{i}'
                i += 1
            self.slug = unique_slug
        
        if self.full_name:
            self.full_name = self.full_name.title()

        if self.education_detail:
            self.education_detail = self.education_detail.title()
        
        if self.note:
            self.note = self.note.capitalize()
        

        super().save(*args, **kwargs)