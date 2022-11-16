import os
from django.db import models
from django.dispatch import receiver

import logging

from goodsmedia.models import Media

logger = logging.getLogger()


@receiver(models.signals.post_delete, sender=Media)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    logger.info('delete file of media %s ' % instance.id)
    if instance.file:
        if os.path.isfile(instance.file.path):
            logger.info('delete file at path %s ' % instance.file.path)
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=Media)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    logger.info('delete file media changed %s ' % instance.id)
    if not instance.pk:
        return False

    try:
        old_file = Media.objects.get(pk=instance.pk).file
    except Media.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

