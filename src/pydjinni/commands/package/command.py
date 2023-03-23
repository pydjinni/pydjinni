import click


@click.command()
def package():
    """Package the compiled binaries for one of the supported platforms"""
    click.echo("package command")