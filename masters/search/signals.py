from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from users.models.master_model import Master
from .documents import MasterDocument
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Master)
def update_master_document(sender, instance, created, **kwargs):
    try:
        # Yeni sənəd yaradılır və məlumatlar köçürülür
        master_doc = MasterDocument(
            meta={'id': instance.id},
            full_name=instance.full_name,  # Modeldəki uyğun sahələri əlavə edin
            experience=instance.experience,
            # Digər lazımi sahələri əlavə edin
        )
        master_doc.save()
        logger.info(f"Master document updated/created for ID: {instance.id}")
    except Exception as e:
        logger.error(f"Error updating master document for ID {instance.id}: {str(e)}")

@receiver(post_delete, sender=Master)
def delete_master_document(sender, instance, **kwargs):
    try:
        doc = MasterDocument.get(id=instance.id)
        doc.delete()
        logger.info(f"Master document deleted for ID: {instance.id}")
    except Exception as e:
        logger.error(f"Error deleting master document for ID {instance.id}: {str(e)}")