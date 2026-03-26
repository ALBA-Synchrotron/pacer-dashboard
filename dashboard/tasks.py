import datetime

from celery import shared_task
from django.db import transaction

from dashboard.models import Message
from dashboard.utils.messages import get_payload_format


@shared_task(queue="dashboard-logging", retry_backoff=True, retry_kwargs={"max_retries": 10})
def log_pacer_message(object_identifiers: dict, processing_start: str, processing_end: str, hash: str,
                      message_type: str,
                      payload_format: str,
                      payload: str, errored: bool, error_message: str) -> None:
    message: Message

    if not payload_format:
        payload_format = get_payload_format(payload)

    msg_defaults: dict = {
        "object_identifiers": object_identifiers, "processing_start": processing_start,
        "processing_end": processing_end, "errored": errored,
        "error_message": error_message, "message_type": message_type, "payload_format": payload_format,
        "payload": payload
    }

    processing_start_date: datetime.datetime = datetime.datetime.fromisoformat(processing_start)
    processing_end_date: datetime.datetime = datetime.datetime.fromisoformat(processing_end)
    processing_seconds: float = (processing_end_date - processing_start_date).total_seconds()

    msg_defaults["processing_time"] = processing_seconds

    with transaction.atomic():
        _ = Message.objects.create(hash=hash, **msg_defaults)
