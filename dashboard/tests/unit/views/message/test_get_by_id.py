from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


from dashboard.models.message import Message
from dashboard.utils.test.generic_view_test_case import GenericViewTest


User = get_user_model()

class MessageViewTestCase(GenericViewTest):
    fixtures: list[str] = ['message.json']
    base_url: str = '/tmpl/messages/'

    def setUp(self):
        super(MessageViewTestCase, self).setUp()

        self.model_class = Message
        self.model_name = "message"

        self.admin_user = User.objects.create_user(username='admin', email='', password='')
        admin_group = Group.objects.get(name="Administrator")
        self.admin_user.groups.add(admin_group)

        self.reader_user = User.objects.create_user(username='reader_user', email='', password='')
        reader_group = Group.objects.get(name="Readers")
        self.reader_user.groups.add(reader_group)

        self.bl06_user = User.objects.create_user(username='bl06_user', email='', password='')
        bl06_group = Group.objects.get(name="BL06")
        self.bl06_user.groups.add(bl06_group)

        self.bl13_user = User.objects.create_user(username='bl13_user', email='', password='')
        bl13_group = Group.objects.get(name="BL13")
        self.bl13_user.groups.add(bl13_group)


    def test_get_by_id(self):
        url: str = self.base_url + self.invalid_id
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        url = self.base_url + str(self.valid_id)
        self.login(self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('user-sync', response.content.decode())

        url = self.base_url + str(self.valid_id)
        self.login(self.reader_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.content)

        url = self.base_url + str(self.valid_id)
        self.login(self.bl06_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.content)

        url = self.base_url + '2'
        self.login(self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('dataset-ingestion', response.content.decode())

        url = self.base_url + '2'
        self.login(self.reader_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('dataset-ingestion', response.content.decode())

        url = self.base_url + '2'
        self.login(self.bl06_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('dataset-ingestion', response.content.decode())

        url = self.base_url + '2'
        self.login(self.bl13_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.content)
