from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.db.models import Avg
from django.core.validators import MaxLengthValidator, MinLengthValidator

from .master_user_manager_model import MasterUserManager
from reviews.models.review_models import Review
from services.models.category_model import Category
from services.models.service_model import Service
from core.models.city_model import City, District
from core.models.education_model import Education
from core.models.language_model import Language
from utils.validators import *
from utils.constants import GENDER_STATUS


class Master(AbstractUser):
    MASTER = 'Master'
    CUSTOMER = 'Customer'
    NONE = 'None'

    ROLE_STATUS = [
    (MASTER, 'Usta'),
    (CUSTOMER, 'Müştəri'),
    ]

    username = None
    first_name = None
    last_name = None
    email = None
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']
    objects = MasterUserManager()
    is_master = models.BooleanField(default=False, verbose_name='Status')
    user_role = models.CharField(choices=ROLE_STATUS)

    profession_category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='category_masters',
        null=True
    )
    profession_service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
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
        on_delete=models.PROTECT,
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
        upload_to='masters/profile_pictures/',
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
    is_active_on_main_page = models.BooleanField(
        default=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    note = models.CharField(
        max_length=1500,
        verbose_name='Qeyd',
        null=True,
         validators=[
            az_letters_validator, 
            not_only_whitespace,
            MinLengthValidator(3),
            MaxLengthValidator(1000),
        ]
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
    
    def average_rating(self):
        """
        Returns the average rating for the master based on all associated reviews.
        Returns an empty string if no ratings are available.
        """
        average = Review.objects.filter(master=self).aggregate(avg=Avg('rating'))['avg']
        if average is None:
            return ''
        return round(average, 2)

    def __str__(self):
        return f'{self.full_name} in {self.user_role} in role'

    @property
    def average_responsible(self):
        """
        Returns the average 'responsible' score from reviews.
        """
        average = Review.objects.filter(master=self).aggregate(avg=Avg('responsible'))['avg']
        if average is None:
            return ''
        return round(average, 2)

    @property
    def average_neat(self):
        """
        Returns the average 'neat' score from reviews.
        """
        average = Review.objects.filter(master=self).aggregate(avg=Avg('neat'))['avg']
        if average is None:
            return ''
        return round(average, 2)

    @property
    def average_time_management(self):
        """
        Returns the average 'time_management' score from reviews.
        """
        average = Review.objects.filter(master=self).aggregate(avg=Avg('time_management'))['avg']
        if average is None:
            return ''
        return round(average, 2)

    @property
    def average_communicative(self):
        """
        Returns the average 'communicative' score from reviews.
        """
        average = Review.objects.filter(master=self).aggregate(avg=Avg('communicative'))['avg']
        if average is None:
            return ''
        return round(average, 2)

    @property
    def average_punctual(self):
        """
        Returns the average 'punctual' score from reviews.
        """
        average = Review.objects.filter(master=self).aggregate(avg=Avg('punctual'))['avg']
        if average is None:
            return ''
        return round(average, 2)

    @property
    def average_professional(self):
        """
        Returns the average 'professional' score from reviews.
        """
        average = Review.objects.filter(master=self).aggregate(avg=Avg('professional'))['avg']
        if average is None:
            return ''
        return round(average, 2)

    @property
    def average_experienced(self):
        """
        Returns the average 'experienced' score from reviews.
        """
        average = Review.objects.filter(master=self).aggregate(avg=Avg('experienced'))['avg']
        if average is None:
            return ''
        return round(average, 2)

    @property
    def average_efficient(self):
        """
        Returns the average 'efficient' score from reviews.
        """
        average = Review.objects.filter(master=self).aggregate(avg=Avg('efficient'))['avg']
        if average is None:
            return ''
        return round(average, 2)

    @property
    def average_agile(self):
        """
        Returns the average 'agile' score from reviews.
        """
        average = Review.objects.filter(master=self).aggregate(avg=Avg('agile'))['avg']
        if average is None:
            return ''
        return round(average, 2)

    @property
    def average_patient(self):
        """
        Returns the average 'patient' score from reviews.
        """
        average = Review.objects.filter(master=self).aggregate(avg=Avg('patient'))['avg']
        if average is None:
            return ''
        return round(average, 2)

    @property
    def review_count(self):
        """
        Returns the total number of reviews for this master.
        """
        return Review.objects.filter(master=self).count()
    
    def save(self, *args, **kwargs):
        """
        Custom save method to:
        - Auto-generate a unique slug from the full name if not set.
        - Title-case the full_name and education_detail.
        - Capitalize the note field.
        """
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