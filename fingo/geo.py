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


def save_image_geo_location(image):
    """Queries Google's GEO API for the location of this Image"""

    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?latlng={},{}'.format(image.geo_lat, image.geo_lon))
    json_data = json.loads(response.text)

    # Pick the first one, this is generally the most specific result
    # https://developers.google.com/maps/documentation/geocoding/intro#ReverseGeocoding
    if not json_data:
        logger.warning('No geo found for %s', str(image))
        return
    try:
        image.geo_formatted_address = json_data['results'][0]['formatted_address']
    except IndexError:
        logger.error('Geo missing for %s', str(image))
        print(json_data['results'])
    try:
        for component in json_data['results'][0]['address_components']:
            if 'route' in component['types']:
                # 'Street'
                image.geo_route = component['long_name']
            elif 'postal_code' in component['types']:
                image.geo_postal_code = component['long_name']
            elif 'locality' in component['types']:
                image.geo_city = component['long_name']
            elif 'administrative_area_level_1' in component['types']:
                image.geo_administrative_area_level_1 = component['long_name']
            elif 'geo_administrative_area_level_2' in component['types']:
                image.geo_administrative_area_level_2 = component['long_name']
            elif 'country' in component['types']:
                image.geo_country = component['long_name']
                image.geo_country_code = component['short_name']
    except IndexError:
        logger.warning('Error while iterating address_components for %s', str(image))

    image.save()
