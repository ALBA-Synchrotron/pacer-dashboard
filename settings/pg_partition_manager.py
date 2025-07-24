from django.conf import settings
from django.apps import apps, AppConfig
from django.db import models
import inspect

from psqlextra.partitioning import PostgresPartitioningManager


def get_model_classes() -> list:
    model_classes: list = []

    for app_name in settings.LOCAL_APPS:
        app_config: AppConfig = apps.get_app_config(app_name.split('.')[-1])
        for model in app_config.get_models():
            if inspect.isclass(model) and issubclass(model, models.Model):
                model_classes.append(model)
    return model_classes


manager: PostgresPartitioningManager = PostgresPartitioningManager(
    [i.get_partition_config() for i in get_model_classes() if
     hasattr(i, "get_partition_config") and callable(i.get_partition_config)]
)
