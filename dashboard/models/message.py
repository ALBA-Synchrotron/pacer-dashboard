from django.db import models
from psqlextra.models import PostgresPartitionedModel
from psqlextra.partitioning import PostgresCurrentTimePartitioningStrategy, PostgresTimePartitionSize, \
    PostgresPartitioningConfig
from psqlextra.types import PostgresPartitioningMethod

from ..labels.message import MODEL_LABELS, VERBOSE_NAME, VERBOSE_NAME_PLURAL


class Message(PostgresPartitionedModel):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=MODEL_LABELS.get("created_at"))
    processing_start = models.DateTimeField(null=True, blank=True, verbose_name=MODEL_LABELS.get("processing_start"))
    processing_end = models.DateTimeField(null=True, blank=True, verbose_name=MODEL_LABELS.get("processing_end"))
    processing_time = models.FloatField(null=True, blank=True, verbose_name=MODEL_LABELS.get("processing_time"))
    hash = models.CharField(max_length=255, null=True, verbose_name=MODEL_LABELS.get("hash"))
    message_type = models.CharField(max_length=255, default="unknown", verbose_name=MODEL_LABELS.get("message_type"))
    object_identifiers = models.JSONField(verbose_name=MODEL_LABELS.get("object_identifiers"), null=True, blank=True)
    payload_format = models.CharField(max_length=255, verbose_name=MODEL_LABELS.get("payload_format"))
    payload = models.JSONField(verbose_name=MODEL_LABELS.get("payload"))
    errored = models.BooleanField(default=False, verbose_name=MODEL_LABELS.get("errored"))
    error_message = models.TextField(null=True, blank=True, verbose_name=MODEL_LABELS.get("error_message"))

    class PartitioningMeta:
        method: str = PostgresPartitioningMethod.RANGE
        key: list = ["created_at"]

    class Meta:
        verbose_name: str = VERBOSE_NAME
        verbose_name_plural: str = VERBOSE_NAME_PLURAL

    @classmethod
    def get_partition_config(cls) -> PostgresPartitioningConfig:
        return PostgresPartitioningConfig(
            model=cls,
            strategy=PostgresCurrentTimePartitioningStrategy(
                size=PostgresTimePartitionSize(months=6),
                count=2
            )
        )
