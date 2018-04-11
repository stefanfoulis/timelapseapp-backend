import json, sys, os

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from eliot import add_destinations, add_global_fields, start_action, Message

from progress_experiment.consumers import PROGRESS_GROUP_NAME


def stdout(message):
    print(message)


def send_to_progress_group(message):
    if 'progress' not in message:
        return
    done = message['progress']['done']
    total = message['progress']['total']
    percentage = int(round(float(done) / float(total) * 100))
    channel_layer = get_channel_layer()
    message = {
        'type': 'progress.update',
        'progress_id': str(message['task_uuid']),
        'progress_name': 'whatever',
        'progress_percentage': percentage,
    }
    print(message)
    async_to_sync(channel_layer.group_send)(
        group=PROGRESS_GROUP_NAME,
        message=message,
    )


with start_action(action_type='logging-init'):
    Message.log(message_type='info', message='adding global fields')
    add_global_fields(
        process_id='{}:{}'.format(sys.argv[0], os.getpid()),
    )
    Message.log(message_type='info', message='adding stdout destination')
    add_destinations(stdout)
    add_destinations(send_to_progress_group)

