import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings


class WSConsumer(AsyncWebsocketConsumer):
    """
    Default shell for a given WebSocket asynchronous connection.
    If not specified it will connect to the apps default room_name.
    You can define specific send/receive methods on Specific Consumers.
    See MessagesConsumer for an example.
    """

    room_name: str = settings.WEBSOCKET_DEFAULT_ROOM_NAME
    room_group_name: str = ""

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs'].get('room_name', self.room_name)
        self.room_group_name = f"{self.room_name}_room"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


class MessagesConsumer(WSConsumer):
    channel_name = "dashboard-messages"

    async def new_message(self, event: dict):
        await self.send(text_data=json.dumps(event))