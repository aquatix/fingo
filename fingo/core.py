# encoding: utf-8

from __future__ import absolute_import

import json
import logging
import os

from fingo import files

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


def clean_images():
    """Iterates through the scaled images and check against the collection if they're still there.
    Removes those variants when needed.
    """
    pass


def clean_collection(collection):
    """Iterates through the images in the Collection and remove those that don't exist
    on disk anymore
    """
    images = collection.images()
    number_purged = 0
    for image in images:
        if not os.path.isfile(image.get_filepath()):
            logger.info('Removing Image %s from collection %s', image.get_filepath(), collection)
            image.delete()
            number_purged = number_purged + 1
    return number_purged


def update_scaled_images(collection):
    """Iterates through the images in the Collection and generates resized versions of images
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


def update_everything(config_file):
    """Iterates through all Collection's, update_collection, remove stale images and scale images
    """
    config = files.load_config(config_file)

    directories, images = files.get_gallery_tree(config['dirs']['image_originals_dir'])

    project_dirs, images_data = files.get_images_metadata(config['dirs']['image_originals_dir'])

    # TODO: get diff between the two with files.get_new_items() and files.get_deleted_items()
    new_items = files.get_new_items()
    # create new metadata files
    # create scaled versions of the images
