from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models.category_model import Category
from .models.service_model import Service


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def clear_category_caches(sender, **kwargs):
    cache.delete('category_list')


@receiver(post_save, sender=Service)
@receiver(post_delete, sender=Service)
def clear_service_caches(sender, **kwargs):
    cache.delete('services_list')


@receiver(post_save, sender=Service)
@receiver(post_delete, sender=Service)
def clear_service_caches_for_category(sender, instance, **kwargs):
    category_id = instance.category_id
    cache_key = f'services_for_category_{category_id}'
    cache.delete(cache_key)