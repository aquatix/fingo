import click

from fingo import core


## Main program
@click.group()
def cli():
    # Lifelog logbook parser
    pass


@cli.command()
@click.option('-c', '--config', prompt='Gallery config file', default=None, type=click.Path(exists=True))
def build_gallery(config):
    """Scans the image dirs, updates the metadata in the project path and generates the site in destination, creating image variants where needed

    config: the yaml file containing the various paths for the project to be used
    """

    paths = core.load_config(config)
