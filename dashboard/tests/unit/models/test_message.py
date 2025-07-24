from dashboard.models import Message
from dashboard.tasks import log_pacer_message
from dashboard.utils.test.generic_test_case import GenericTestCase


class MessageLoggingTestCase(GenericTestCase):

    def setUp(self) -> None:
        super(MessageLoggingTestCase, self).setUp()

        self.model_class = Message

        self.mandatory_fields_json = {
            "created_at": "2025-07-24T07:31:47.238Z",
            "processed_at": "2025-07-24T07:31:47.184Z",
            "hash": "02ac1b88a233cdf131b74f8e7dfe8cd9f4531a9db25ccbf1ef30d36ac5a08422",
            "message_type": "user-sync",
            "object_identifiers": {},
            "payload_format": "unknown",
            "payload": "{\"first_name\": \"GAURAV\", \"last_name\": \"MUDGAL\", \"ORCID\": null, \"email\": \"gauravmdgl@gmail.com\", \"affiliation\": {\"id\": 62, \"name\": \"Consejo Superior de Investigaciones Científicas\", \"code\": \"CSIC\", \"department_name\": \"Centro Nacional de Biotecnología\", \"department_code\": \"CNB\", \"unit\": \"Estructura de Macromoléculas\", \"city\": \"Madrid\", \"country_code\": \"ES\"}, \"is_staff\": false, \"enabled\": true, \"id\": 39, \"user_list\": }",
            "errored": True,
            "error_message": "[('__broker_forwarder_callback', TypeError(\"PACERConsumer.__broker_forwarder_callback() got an unexpected keyword argument 'errors'\"))]"
        }

    def test_log_message(self) -> None:
        num_objects: int = self.model_class.objects.count()
        self.assertEqual(num_objects, 0)
        log_pacer_message(
            self.mandatory_fields_json.get("object_identifiers"),
            self.mandatory_fields_json.get("processed_at"),
            self.mandatory_fields_json.get("hash"),
            self.mandatory_fields_json.get("message_type"),
            self.mandatory_fields_json.get("payload_format"),
            self.mandatory_fields_json.get("payload"),
            self.mandatory_fields_json.get("errored"),
            self.mandatory_fields_json.get("error_message")
        )

        num_objects: int = self.model_class.objects.count()
        self.assertEqual(num_objects, 1)

        obj = self.model_class.objects.get(hash=self.mandatory_fields_json.get("hash"))
        self.assertEqual(obj.error_message, self.mandatory_fields_json.get("error_message"))
