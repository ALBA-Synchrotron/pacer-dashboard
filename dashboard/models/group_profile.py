from django.contrib.auth.models import User
from django.db import models
from django.core.cache import cache
from django.db.models import QuerySet, Q

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

    class Meta:
        verbose_name: str = VERBOSE_NAME
        verbose_name_plural: str = VERBOSE_NAME_PLURAL

    @classmethod
    def get_user_filters(cls, user: User) -> Q:
        cache_key: str = f"{user.username}_profile_filters"
        query: Q = cache.get(cache_key, Q())
        if query:
            return query

        profiles: QuerySet = user.groups.select_related("groupprofile").all()
        allowed_msg_types: str = ",".join(
            i.groupprofile.allowed_message_types for i in profiles if i.groupprofile.allowed_message_types)
        allowed_object_identifiers: str = ",".join(
            i.groupprofile.allowed_object_identifiers for i in profiles if i.groupprofile.allowed_object_identifiers)

        if allowed_msg_types:
            query &= Q(message_type__in=allowed_msg_types.split(","))

        if allowed_object_identifiers:
            query &= Q(object_identifiers__instrument__in=allowed_object_identifiers.split(","))

        return query
