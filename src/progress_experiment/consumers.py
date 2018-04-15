import json
import uuid

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer


PROGRESS_GROUP_NAME = 'progress_group'


class ProgressConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.progress_group_name = PROGRESS_GROUP_NAME
        async_to_sync(self.channel_layer.group_add)(
            group=self.progress_group_name,
            channel=self.channel_name
        )
        self.accept()
        # self.send_json(
        #     content={
        #         'progress_uuid': str(uuid.uuid4()),
        #         'action_type': 'Hello World',
        #         'message_type': 'huh?',
        #         'progress_percentage': 50,
        #     }
        # )
        # self.send_json(
        #     content={
        #         'progress_uuid': str(uuid.uuid4()),
        #         'action_type': 'Foo',
        #         'message_type': 'Bar?',
        #         'progress_percentage': 75,
        #     }
        # )

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.progress_group_name,
            self.channel_name
        )

    def receive_json(self, content):
        pass

    def progress_update(self, event):
        self.send_json(content=event)
