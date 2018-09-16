# encoding: utf-8

from __future__ import absolute_import

import logging
import os
from PIL import Image as PILImage, ImageFile as PILImageFile, ExifTags
from datetime import datetime
import exifread
import imagehash
import json
import pytz
import requests

try:
    DEBUG = settings.DEBUG
except NameError:
    DEBUG = True
    #DEBUG = False

logger = logging.getLogger('fingo')
logger.setLevel(logging.DEBUG)
lh = logging.StreamHandler()
if DEBUG:
    lh.setLevel(logging.DEBUG)
else:
    lh.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
lh.setFormatter(formatter)
logger.addHandler(lh)


def scale_image(image_id, destination_dir, width, height, crop=False):
    """
    Create scaled versions of the Image with image_id
    """
    image = Image.objects.get(pk=image_id)
    if not image.image_hash:
        logger.info('No hash found for Image with pk %d', image.pk)
        return
    filename_base = os.path.join(destination_dir, image.image_hash[:2], image.image_hash)
    util.ensure_dir_exists(filename_base)
    variant = '_{}-{}.{}'.format(width, height, image.file_ext)
    if os.path.isfile(filename_base + variant):
        #logger.debug('Skipping resize for existing %s%s', filename_base, variant)
        return

    logger.info('resizing into %s', filename_base + variant)
    # TODO: be more clever with the config
    if width == 0:
        raise Exception('width can not be zero')
    if height == 0:
        raise Exception('height can not be zero')
    try:
        im = PILImage.open(image.get_filepath())
        im.thumbnail((width, height))
        if image.file_ext == 'jpg' or image.file_ext == 'jpeg':
            if width >= settings.EXIF_COPY_THRESHOLD or height >= settings.EXIF_COPY_THRESHOLD:
                # If variant is larger than the set threshold, copy EXIF tags
                # Smaller variants effectively get EXIF stripped so resulting files are smaller
                # (good for thumbnails)
                try:
                    exif = im.info['exif']
                    im.save(filename_base + variant, 'JPEG', exif=exif)
                except KeyError:
                    # No EXIF found, save normally
                    im.save(filename_base + variant, 'JPEG')
            else:
                im.save(filename_base + variant, 'JPEG')
        elif image.file_ext == 'png':
            im.save(filename_base + variant, 'PNG')
    except IOError:
        logger.info('Cannot create %dx%d variant for %s', width, height, image)


def update_scaled_images(collection):
    """
    Iterate through the images in the Collection and generate resized versions of images
    that don't have those yet
    """
    images = collection.images()
    variants = PhotoSize.objects.all()
    if len(variants) == 0:
        logger.info('No size variants defined, configure some PhotoSizes')
        return
    for image in images:
        for variant in variants:
            scale_image(image.pk, collection.archive_dir, variant.width, variant.height, variant.crop_to_fit)
