import json
import os
import sys

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from eliot import Message, add_destinations, add_global_fields, start_action, to_file

from progress_experiment.consumers import PROGRESS_GROUP_NAME


def stdout(message):
    print(message)


def send_to_progress_group(message):
    if "progress" not in message:
        return
    done = message["progress"]["done"]
    total = message["progress"]["total"]
    percentage = int(round(float(done) / float(total) * 100))
    channel_layer = get_channel_layer()
    root_task_uuid = str(message["task_uuid"])
    tree = [root_task_uuid] + message["task_level"]
    combined_task_uuid = "--".join([str(x) for x in tree])
    progress_task_uuid = "--".join([str(x) for x in tree[:-1]])
    message = {
        "type": "progress.update",
        # 'task_uuid': root_task_uuid,
        "progress_uuid": progress_task_uuid,
        "progress_name": "whatever",
        "progress_percentage": percentage,
        "action_type": message.get("action_type", ""),
        "message_type": message.get("message_type", ""),
    }
    print(message)
    async_to_sync(channel_layer.group_send)(group=PROGRESS_GROUP_NAME, message=message)


# add_global_fields(
#     process_id='{}:{}'.format(sys.argv[0], os.getpid()),
# )
add_destinations(stdout)
add_destinations(send_to_progress_group)
to_file(open("/app/tmp/timelapse.log", "ab"))
