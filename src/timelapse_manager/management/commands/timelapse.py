import djclick as click

from timelapse_manager.storage import dsn_variable_configured_storage

from ... import actions, models


@click.group()
def command():
    pass


@command.command(name="import", help="Import images")
@click.option(
    "--path", type=click.Path(exists=True), help="The filesystem path to import from"
)
@click.option("--stream-id", help="Stream id")
def import_images(path, stream_id):
    storage = dsn_variable_configured_storage(f"file://{path}")
    stream = models.Stream.objects.get(pk=stream_id)
    actions.import_images(stream=stream, storage=storage, path="")
