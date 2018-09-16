# encoding: utf-8

from __future__ import absolute_import

import logging
import os
from django.conf import settings
from imagine.models import Collection, Directory, Image, ImageMeta, PhotoSize, ExifItem
from imagine import util
from PIL import Image as PILImage, ImageFile as PILImageFile, ExifTags
from datetime import datetime
import exifread
import imagehash
import json
import pytz
import requests

def get_filename(directory, filename):
    """Return (filename, extension) of the file in filename"""

    #newFilename, fileExtension = os.path.splitext(filename)[1][1:].strip()
    #print os.path.splitext(filename)[1][1:].strip()
    extension = os.path.splitext(filename)[1][1:].strip().lower()
    #print '[Info] {0} - {1}'.format(filename, fileExtension)

    new_filename = filename.replace(directory, '')
    return (new_filename, extension)


def update_collection(collection):
    """ Creates a new image archive in archive_dir
    """
    #logger.debug('Writing archive to %s', archive_dir)
    #logger.debug('images_dir: %s', images_dir,'')

    #create_archive()
    #collection, created = Collection.get_or_create(name=collection_name, slug=collection_slug, base_dir=images_dir)
    #logger.debug('Collection created: %s', str(created))
    _walk_archive(collection)


def _update_directory_parents(collection):
    """
    Correctly assign parent directories to the various directory objects
    """
    directory_list = Directory.objects.filter(collection=collection).order_by('directory')

    for directory in directory_list:
        # If relative_path is empty, it's the root of the collection, otherwise assign a parent
        if not directory.relative_path:
            directory.parent_directory = None  # root of Collection
            directory.save()
        else:
            parent_directory_path = os.path.abspath(os.path.join(directory.directory, os.pardir)) + '/'
            directory.parent_directory = Directory.objects.get(directory=parent_directory_path)
            directory.save()


def _walk_archive(collection):
    image_counter = 0
    skipped_counter = 0
    total_files = 0
    created_dirs = 0
    for dirname, _dirnames, filenames in os.walk(collection.base_dir):
        this_dir = os.path.join(dirname, '')  # be sure to have trailing / and such
        full_dir = this_dir
        #logger.debug(this_dir)
        this_dir = this_dir.replace(collection.base_dir, '')
        if this_dir[0] == '/':
            this_dir = this_dir[1:]
        if this_dir and this_dir[-1] == '/':
            this_dir = this_dir[:-1]
        directory, created = Directory.objects.get_or_create(directory=full_dir, relative_path=this_dir, collection=collection)
        logger.debug('Directory %s created: %s', full_dir, str(created))
        if created:
            created_dirs = created_dirs + 1
        #for subdirname in dirnames:
        #    logger.debug('dir: %s', os.path.join(dirname, subdirname))
        total_files = total_files + len(filenames)
        for filename in filenames:
            #print os.path.join(dirname, filename)
            this_file, this_file_ext = get_filename(collection.base_dir, os.path.join(dirname, filename))
            this_path = os.path.dirname(this_file)
            this_file = this_file.replace(this_dir, '')
            #logger.debug('ext: %s', this_file_ext)
            if this_file_ext in Image.IMAGE_EXTENSIONS:
                the_image, created = Image.objects.get_or_create(
                    collection=collection,
                    directory=directory,
                    filename=filename,
                    file_ext=this_file_ext,
                    file_path=this_path,
                )
                if created:
                    # Only save if new image
                    save_image_info(the_image, os.path.join(dirname, filename), this_file_ext)
                    logger.info('created Image for %s', the_image)
                    image_counter = image_counter + 1
                else:
                    skipped_counter = skipped_counter + 1
                    #logger.debug('skipped Image for %s', the_image)
                the_image_hash, created = ImageMeta.objects.get_or_create(image_hash=the_image.image_hash)
            else:
                #logger.info('skipped %s', filename)
                pass

    logger.info('added %d images to archive out of %d total, skipped %d; created %d directories', image_counter, total_files, skipped_counter, created_dirs)

    #if created_dirs:
    _update_directory_parents(collection)

    return image_counter, total_files, skipped_counter


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
