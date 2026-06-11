from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings


@receiver(pre_save, sender=User)
def user_role_changed(instance, **_kwargs):
    for cache_key_suffix in settings.USER_CACHE_KEYS_SUFFIX.values():
        cache_key: str = f"{instance.username}{cache_key_suffix}"
        cache.delete(cache_key)
