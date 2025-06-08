from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from users.models.master_model import CustomerUser
from .documents import CustomerUserDocument 

@receiver(post_save, sender=CustomerUser)
def update_master_document(sender, instance, **kwargs):
    if instance.user_role == CustomerUser.MASTER:  
        doc = CustomerUserDocument(meta={'id': instance.id})
        doc.user_role = instance.user_role
        doc.is_master = instance.is_master
        doc.save()
    else:
        try:
            doc = CustomerUserDocument.get(id=instance.id)
            doc.delete()
        except Exception:
            pass


@receiver(post_delete, sender=CustomerUser)
def delete_master_document(sender, instance, **kwargs):
    try:
        doc = CustomerUserDocument.get(id=instance.id)
        doc.delete()
    except Exception:
        pass