# encoding: utf-8

from __future__ import absolute_import

import json
import logging
import os

import yaml

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


def load_config(config_file):
    """
    project_dir: directory where the gallery metadata lives
    output_dir: generated website
    image_originals_dir: source of the original version of the images
    image_output_dir: generated (scaled) images
    template_dir: directory of the template to be used for the generated site
    """
    try:
        f = open(config_file)

        print('r Reading structure from ' + os.path.join(site, 'site.yaml'))

        structure = fileutil.yaml_ordered_load(f, yaml.SafeLoader)
        f.close()
    except IOError as e:
        print(e)
        sys.exit(1)


def clean_collection(collection):
    """
    Iterate through the images in the Collection and remove those that don't exist
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


def update_everything():
    """
    Iterate through all Collection's, update_collection, remove stale images and scale images
    """
    collections = Collection.objects.all()
    for collection in collections:
        update_collection(collection)
        clean_collection(collection)
        update_scaled_images(collection)
