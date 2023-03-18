import click

from main import create_app
from main.settings import Config

app = create_app()
app.app_context().push()


@click.group()
def cli():
    pass


@cli.command()
def rest():
    click.echo('Run server')
    app.run()


if __name__ == '__main__':
    cli()
