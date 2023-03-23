import click


@click.command()
def init():
    """Create a new pydjinni project from scratch."""
    click.echo("init command")