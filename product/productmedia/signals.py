import os
from django.db import models
from django.dispatch import receiver

import logging

from productmedia.models import Media, ProductMedia, ProductOptionMedia

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


@receiver(models.signals.pre_delete, sender=ProductMedia)
def auto_delete_media_on_delete(sender, instance: ProductMedia, **kwargs):
    logger.info('post delete product media object ,delete media ')
    media = instance.media
    if instance.media:
        relative_option = getattr(media, Media.RelativeFields.MEDIA_OPTIONS).all()
        relative_product = getattr(media, Media.RelativeFields.MEDIA_PRODUCTS).all()
        if relative_option.count() <= 0 and relative_product.count() <= 0:
            logger.warning('Delete media of id %s ' % media.id)
            media.delete()
        else:
            logger.info('Can not delete media yet, has relative object')


@receiver(models.signals.post_delete, sender=ProductOptionMedia)
def auto_delete_option_media_on_delete(sender, instance: ProductOptionMedia, **kwargs):
    logger.info('post delete product media object ,delete media ')
    media = instance.media
    if instance.media:
        relative_option = getattr(media, Media.RelativeFields.MEDIA_OPTIONS).all()
        relative_product = getattr(media, Media.RelativeFields.MEDIA_PRODUCTS).all()
        if relative_option.count() <= 0 and relative_product.count() <= 0:
            logger.warning('Delete media of id %s ' % media.id)
            media.delete()
        else:
            logger.info('Can not delete media yet, has relative object')
