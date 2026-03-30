from django.conf import settings

def django_settings(_request) -> dict:
    return {
        "DISABLED_AUTH": settings.DISABLED_AUTH
    }
