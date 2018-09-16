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


def save_jpg_exif(image, filename):
    """Fetch exif tags for the image Image object from the .jpg in filename"""
    # Open image file for reading (binary mode)
    f = open(filename, 'rb')

    datetime_taken = None
    geo = {}

    # Return Exif tags
    exif = exifread.process_file(f)
    for k, v in exif.items():
        try:
            if 'thumbnail' in k.lower():
                #logger.debug('Skipping thumbnail exif item for %s', filename)
                continue
            exif_item = ExifItem(
                    image=image,
                    key=k,
                    value_str=v
            )
            exif_item.save()
            if k == 'EXIF DateTimeOriginal':
                datetime_taken = str(v)
            if k == 'GPS GPSLatitude':
                geo['GPS GPSLatitude'] = v
            if k == 'GPS GPSLatitudeRef':
                geo['GPS GPSLatitudeRef'] = v
            if k == 'GPS GPSLongitude':
                geo['GPS GPSLongitude'] = v
            if k == 'GPS GPSLongitudeRef':
                geo['GPS GPSLongitudeRef'] = v
        except UnicodeDecodeError:
            logger.warning('Failed to save exif item %s due to UnicodeDecodeError', k)
    return datetime_taken, geo


def save_cr2_exif(image, filename):
    """Fetch exif tags for the image Image object from the .cr2 raw file in filename"""
    logger.warning('cr2 metadata support not implemented yet')


def save_image_info(the_image, filename, file_ext):
    """Create/update Image object from the image in filename"""

    the_image.filesize = os.stat(filename).st_size
    the_image.save()

    if file_ext not in Image.IMAGE_EXTENSIONS_RAW:
        try:
            image = PILImage.open(filename)
            the_image.image_hash = imagehash.dhash(image)

            the_image.width = image.size[0]
            the_image.height = image.size[1]

            # Done with image info for now, save
            the_image.save()
        except IOError:
            logger.error('IOError opening %s', filename)

    exif_datetime_taken = None

    if file_ext == 'jpg':
        exif_datetime_taken, geo_exif_items = save_jpg_exif(the_image, filename)
    elif file_ext == 'cr2':
        save_cr2_exif(the_image, filename)
    else:
        logger.warning('No supported extension found')

    #the_image.file_modified = datetimeutil.unix_to_python(os.path.getmtime(filename))
    the_image.file_modified = datetime.fromtimestamp(float((os.path.getmtime(filename))), tz=pytz.utc)

    if exif_datetime_taken:
        #the_image.exif_modified = datetimeutil.load_datetime(exif_datetime_taken, '%Y:%m:%d %H:%M:%S')
        the_image.exif_modified = util.load_datetime(exif_datetime_taken, '%Y:%m:%d %H:%M:%S').replace(tzinfo=pytz.utc)
        the_image.filter_modified = the_image.exif_modified
    else:
        the_image.filter_modified = the_image.file_modified

    try:
        if geo_exif_items:
            lat, lon = util.get_exif_location(geo_exif_items)
            the_image.geo_lat = lat
            the_image.geo_lon = lon
            # TODO: create config item to enable/disable geo lookups
            # Do request to http://maps.googleapis.com/maps/api/geocode/xml?latlng=53.244921,-2.479539&sensor=true
            save_image_geo_location(the_image)
    except UnboundLocalError:
        # No geo data
        pass

    the_image.save()

    # TODO: update exif highlights fields from EXIF tags
    # exifhighlights = self.get_exif_highlights()

    #exif = {
    #        ExifTags.TAGS[k]: v
    #        for k, v in image._getexif().items()
    #        if k in ExifTags.TAGS
    #}
    #print(exif)
    #file = open(filename, 'r')
    #parser = PILImageFile.Parser()

    #while True:
    #	s = file.read(1024)
    #	if not s:
    #		break
    #	parser.feed(s)
    #image = parser.close()


    #print image.size

    #rw, rh = image.size()
    #print image.size

#	print image.fileName()
#	print image.magick()
#	print image.size().width()
#	print image.size().height()
