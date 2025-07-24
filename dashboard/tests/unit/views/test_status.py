from django.urls import reverse
from rest_framework import status

from dashboard.utils.test.generic_view_test_case import GenericViewTest


class StatusViewTest(GenericViewTest):

    def setUp(self) -> None:
        super(StatusViewTest, self).setUp()
        self.reference_name = "status"

    def test_status(self) -> None:
        url = reverse(self.reference_name)
        self.login_and_check_http_methods(self.authorized_username, url, ['GET'])
        response = self.client.get(url)
        self.assertEqual(str(response.status_code), str(status.HTTP_200_OK))