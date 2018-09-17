import click

from fingo import core


def load_config(config_file):
    pass


## Main program
@click.group()
def cli():
    # Lifelog logbook parser
    pass


@cli.command()
@click.option('-p', '--projectpath', prompt='Gallery path', type=click.Path(exists=True))
@click.option('-d', '--destination', prompt='Destination path', type=click.Path(exists=True))
@click.option('-c', '--config', prompt='Gallery config file', default=None, type=click.Path(exists=True))
def build_gallery(path, destination, config):
    """Scans the image dirs, updates the metadata in the project path and generates the site in destination, creating image variants where needed

    projectpath: directory where the project metadata lives; site config and image metadata files
    destination: 
    """
    pass
