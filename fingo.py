import click
import yaml



def 


## Main program
@click.group()
def cli():
    # Lifelog logbook parser
    pass


@cli.command()
@click.option('-p', '--path', prompt='Gallery path', type=click.Path(exists=True))
@click.option('-d', '--destination', prompt='Destination path', type=click.Path(exists=True))
@click.option('-c', '--config', prompt='Gallery config file', default=None, type=click.Path(exists=True))
def build_gallery(path, destination, config):
    pass
