from celery import shared_task
from django.db import transaction

from dashboard.models import Message
from dashboard.utils.messages import get_payload_format


@shared_task(queue="dashboard-logging", retry_backoff=True, retry_kwargs={"max_retries": 10})
def log_pacer_message(object_identifiers: dict, processed_at: str, hash: str, message_type: str,
                      payload_format: str,
                      payload: str, errored: bool, error_message: str) -> None:
    message: Message

    if not payload_format:
        payload_format = get_payload_format(payload)

    msg_defaults: dict = {
        "object_identifiers": object_identifiers, "processed_at": processed_at, "errored": errored,
        "error_message": error_message, "message_type": message_type, "payload_format": payload_format,
        "payload": payload
    }

    with transaction.atomic():
        _ = Message.objects.create(hash=hash, **msg_defaults)
