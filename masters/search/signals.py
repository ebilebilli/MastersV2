from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from users.models.master_model import Master
from .documents import MasterDocument 

@receiver(post_save, sender=Master)
def update_master_document(sender, instance, **kwargs):
    if instance.user_role == 'master':  # sadəcə rolu 'master' olanları indeksləyir
        doc = MasterDocument(meta={'id': instance.id})
        doc.user_role = instance.user_role
        doc.is_master = instance.is_master
        doc.save()
    else:
        try:
            doc = MasterDocument.get(id=instance.id)
            doc.delete()
        except Exception:
            pass


@receiver(post_delete, sender=Master)
def delete_master_document(sender, instance, **kwargs):
    try:
        doc = MasterDocument.get(id=instance.id)
        doc.delete()
    except Exception:
        pass