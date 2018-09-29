import djclick as click

from timelapse_manager.storage import dsn_variable_configured_storage

from ... import actions, models


@click.group()
def command():
    pass


@command.command(name="import-images-from-local-filesystem", help="Import images")
@click.option(
    "--path", type=click.Path(exists=True), help="The filesystem path to import from"
)
@click.option("--stream-id", help="Stream id")
def import_images_from_local_filesystem(path, stream_id):
    storage = dsn_variable_configured_storage(f"file://{path}")
    stream = models.Stream.objects.get(pk=stream_id)
    actions.import_images(stream=stream, storage=storage, path="")


@command.command(name="discover-images", help="Import images")
@click.option(
    "--stream-dir", help="The relative path of the stream in the default storage"
)
@click.option("--stream-id", help="Stream id")
def discover_images_on_storage(stream_dir, stream_id=None):
    actions.discover_images(stream_dir=stream_dir, stream=stream_id)
