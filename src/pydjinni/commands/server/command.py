import click


@click.command()
@click.pass_context
def server(ctx):
    """Starts a language server"""
    print("starting lsp server")
