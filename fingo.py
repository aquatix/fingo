import click

from fingo import core


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
