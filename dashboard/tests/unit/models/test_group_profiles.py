from django.contrib.auth.models import User, Group

from dashboard.models import GroupProfile, Message
from dashboard.utils.test.generic_test_case import GenericTestCase


class GroupProfileTestCase(GenericTestCase):
    fixtures = ["message.json"]

    def test_admin_permissions(self) -> None:
        user, _ = User.objects.get_or_create(username="test_user_admin")
        assert user.groups.count() == 0
        admin_group = Group.objects.get(name="Administrator")
        user.groups.add(admin_group)

        assert user.groups.count() == 1

        filters = GroupProfile.get_user_filters(user)
        assert Message.objects.filter(filters).count() == Message.objects.count()

    def test_reader_permissions(self) -> None:
        user, _ = User.objects.get_or_create(username="test_user_readers")
        assert user.groups.count() == 0
        reader_group = Group.objects.get(name="Readers")
        user.groups.add(reader_group)
        assert user.groups.count() == 1

        filters = GroupProfile.get_user_filters(user)
        msgs = Message.objects.filter(filters)
        assert all(i.message_type in i.message_type in reader_group.groupprofile.allowed_message_types.split(",") for i in msgs)

    def test_bl_permissions(self) -> None:
        user, _ = User.objects.get_or_create(username="test_user_bl04")
        assert user.groups.count() == 0
        reader_group = Group.objects.get(name="BL04")
        user.groups.add(reader_group)

        assert user.groups.count() == 1

        filters = GroupProfile.get_user_filters(user)
        msgs = Message.objects.filter(filters)
        assert all(
            i.message_type in i.message_type in reader_group.groupprofile.allowed_message_types.split(",") for i in
            msgs)
        assert all("BL04" in str(i.object_identifiers) for i in msgs)