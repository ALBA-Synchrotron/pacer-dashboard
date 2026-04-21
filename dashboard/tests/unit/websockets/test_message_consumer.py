from django.test import TransactionTestCase
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from settings.asgi import application
import asyncio

class MessageConsumerTests(TransactionTestCase):

    def test_message_reaches_client_from_group(self):
        async def run_test():
            communicator = WebsocketCommunicator(application, "s/ws/messages/")
            connected, _ = await communicator.connect()
            self.assertTrue(connected)

            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                "messages_room",
                {
                    "type": "new.message",
                    "message_id": 1,
                }
            )

            response = await communicator.receive_json_from()
            self.assertTrue("type" in response)
            self.assertEqual(response["type"], "new.message")
            self.assertEqual(response["message_id"], 1)

            await communicator.disconnect()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_test())