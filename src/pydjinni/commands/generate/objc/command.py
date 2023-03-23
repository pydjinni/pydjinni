import click
from logging import Logger
from pydjinni.context import pass_logger, pass_generate_context, GenerateContext

@click.command()
@pass_generate_context
@pass_logger
@click.pass_context
def objc(ctx, logger: Logger, generate_context: GenerateContext):
    """Generate Java glue-code"""
    logger.info("generate java glue-code")

