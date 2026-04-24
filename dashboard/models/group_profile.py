from django.contrib.auth.models import User
from django.db import models
from django.core.cache import cache
from django.db.models import QuerySet, Q
from psqlextra.query import PostgresQuerySet

from . import Message
from ..labels.group_profile import MODEL_LABELS, VERBOSE_NAME, VERBOSE_NAME_PLURAL


class GroupProfile(models.Model):
    group = models.OneToOneField(
        "auth.Group",
        on_delete=models.CASCADE,
        verbose_name=MODEL_LABELS.get("group"),
    )
    allowed_message_types = models.CharField(max_length=255, blank=True, null=True,
                                             verbose_name=MODEL_LABELS.get("allowed_message_types"))
    allowed_object_identifiers = models.CharField(max_length=255, blank=True, null=True,
                                                  verbose_name=MODEL_LABELS.get("allowed_object_identifiers"))
    msg_actions_allowed = models.BooleanField(default=False, verbose_name=MODEL_LABELS.get("msg_actions_allowed"))

    class Meta:
        verbose_name: str = VERBOSE_NAME
        verbose_name_plural: str = VERBOSE_NAME_PLURAL

    @classmethod
    def get_allowed_message_types(cls, user: User):
        cache_key: str = f"{user.username}_ui_profile_filters"
        ui_filters = cache.get(cache_key, None)
        if ui_filters:
            return ui_filters

        profiles = [i.groupprofile for i in user.groups.select_related("groupprofile").all() if hasattr(i, "groupprofile")]

        allowed_msg_types = {mt.strip() for profile in profiles if profile.allowed_message_types for mt in profile.allowed_message_types.split(",")}

        if not allowed_msg_types:
            msg_types = list(
                Message.objects.filter()
                .values_list("message_type", flat=True)
                .distinct()
            )
        else:
            msg_types = list(
                Message.objects.filter(message_type__in=allowed_msg_types)
                .values_list("message_type", flat=True)
                .distinct()
            )

        cache.set(cache_key, msg_types, 60 * 60 * 24)
        return msg_types

    @classmethod
    def get_user_filters(cls, user: User) -> Q:
        cache_key: str = f"{user.username}_query_profile_filters"
        query: Q = cache.get(cache_key, None)
        if query:
            return query

        query = Q()

        if not "Administrator" in [i.name for i in user.groups.all()] or user.groups.count() == 0:

            profiles: QuerySet = user.groups.select_related("groupprofile").all()
            allowed_msg_types: str = ",".join(
                i.groupprofile.allowed_message_types for i in profiles if i.groupprofile.allowed_message_types)
            allowed_object_identifiers: str = ",".join(
                i.groupprofile.allowed_object_identifiers for i in profiles if
                i.groupprofile.allowed_object_identifiers)

            if allowed_msg_types:
                query &= Q(message_type__in=allowed_msg_types.split(","))

            if allowed_object_identifiers:
                query &= Q(object_identifiers__instrument__in=allowed_object_identifiers.split(","))

            cache.set(cache_key, query, timeout=60 * 60 * 24)

        return query
