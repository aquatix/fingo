import logging

import click

from fingo import core

# create logger with 'spam_application'
logger = logging.getLogger('fingo')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('fingo.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

## Main program
@click.group()
def cli():
    # fingo static gallery website generator
    pass


@cli.command()
@click.option('-c', '--config', prompt='Gallery config file', default=None, type=click.Path(exists=True))
def update_collection(config):
    """Scans the image dirs and updates the metadata in the project path.

    config: the yaml file containing the various paths for the project to be used
    """
    click.secho('Needs implementing', fg='red')


@cli.command()
@click.option('-c', '--config', prompt='Gallery config file', default=None, type=click.Path(exists=True))
def scale_images(config):
    """Gets updated images from project and create scaled versions.

    config: the yaml file containing the various paths for the project to be used
    """
    click.secho('Needs implementing', fg='red')


@cli.command()
@click.option('-c', '--config', prompt='Gallery config file', default=None, type=click.Path(exists=True))
def clean_images(config):
    """Gets deleted images from project and remove metadata and scaled versions.

    config: the yaml file containing the various paths for the project to be used
    """
    click.secho('Needs implementing', fg='red')


@cli.command()
@click.option('-c', '--config', prompt='Gallery config file', default=None, type=click.Path(exists=True))
def generate(config):
    """Just generates the site in the destination dir (html and other static assets only, not the images).

    config: the yaml file containing the various paths for the project to be used
    """
    click.secho('Needs implementing', fg='red')


@cli.command()
@click.option('-c', '--config', prompt='Gallery config file', default=None, type=click.Path(exists=True))
def build_gallery(config):
    """Updates and generates everything: scans the image dirs, updates the metadata in the project path and generates
    the site in destination, creating image variants where needed

    config: the yaml file containing the various paths for the project to be used
    """
    core.update_everything(config)


if __name__ == '__main__':
    cli()
