# encoding: utf-8

import os
from collections import OrderedDict

import yaml


def yaml_ordered_load(stream, Loader=None, object_pairs_hook=OrderedDict):
    """
    Load yaml mappings into OrderedDict instead of the unordered vanilla dict type
    source: http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts
    """
    import yaml
    if not Loader:
        Loader = yaml.Loader
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def get_filename(directory, filename):
    """Returns (filename, extension) of the file in filename"""

    extension = os.path.splitext(filename)[1][1:].strip().lower()
    new_filename = filename.replace(directory, '')
    return (new_filename, extension)


def get_project_dirs(config_file):
    """Loads path information from config file

    Args:
        config_file (str): the path to the file containing the project's paths

    Returns:
        List with the paths relevant for the project:
            project_dir: directory where the gallery metadata lives
            output_dir: generated website
            image_originals_dir: source of the original version of the images
            image_output_dir: generated (scaled) images
            template_dir: directory of the template to be used for the generated site

    Raises:
        FileNotFoundError: An error occurred loading the config file
    """
    with open(config_file) as f:
        dirs = yaml_ordered_load(f, yaml.SafeLoader)
    return dirs


def load_config(config_file):
    """Loads the project configuration

    Args:
        config_file (str): the path to the file containing the project's paths

    Returns:
        OrderedDict with title, author and such for gallery, and the paths relevant for the project

    Raises:
        FileNotFoundError: An error occurred loading the config file(s)
    """
    dirs = get_project_dirs(config_file)

    with open(os.path.join(dirs['project_dir'], 'config.yaml')) as f:
        gallery_conf = yaml_ordered_load(f, yaml.SafeLoader)

    # Insert the various project paths
    gallery_conf['dirs'] = dirs
    return gallery_conf


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
