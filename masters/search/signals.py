from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from users.models.master_model import Master
from .documents import MasterDocument 

@receiver(post_save, sender=Master)
def update_master_document(sender, instance, **kwargs):
    MasterDocument().update(instance)

@receiver(post_delete, sender=Master)
def delete_master_document(sender, instance, **kwargs):
    MasterDocument().delete(instance)
