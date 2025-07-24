from dashboard.models import Message
from dashboard.utils.test.generic_model_test_case import GenericModelTestCase


class MessageTestCase(GenericModelTestCase):
    fixtures: list = ["message.json"]

    def setUp(self) -> None:
        super(MessageTestCase, self).setUp()

        self.model_class = Message
        self.model_name = "message"

        self.mandatory_fields_json = {
            "hash": "1234567890",
            "processed_at": "2021-01-01T00:00:00Z",
            "message_type": "test",
            "payload_format": "test",
            "payload": "test"
        }
        self.update_json = {
            "processed_at": "2022-01-01T00:00:00Z",
            "message_type": "test-updated",
        }

    def test_log_message(self) -> None:
        self.create()