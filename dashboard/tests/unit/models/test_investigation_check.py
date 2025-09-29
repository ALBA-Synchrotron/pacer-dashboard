from dashboard.models import Message
from dashboard.tasks import log_pacer_message
from dashboard.utils.test.generic_model_test_case import GenericModelTestCase
from dashboard.utils.test.generic_test_case import GenericTestCase


class InvestigationCheckTestCase(GenericModelTestCase):

    def setUp(self) -> None:
        super(InvestigationCheckTestCase, self).setUp()

        self.model_class = Message

        self.mandatory_fields_json = {
           "investigation": "2025999920"
        }

    def test_create(self) -> None:
        self.create()
