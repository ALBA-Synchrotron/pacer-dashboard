import datetime
import json

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import transaction

from dashboard.models import Message
from dashboard.utils.messages import get_payload_format


@shared_task(queue="dashboard-logging", retry_backoff=True, retry_kwargs={"max_retries": 10})
def log_pacer_message(object_identifiers: dict, processing_start: str, processing_end: str, hash: str,
                      message_type: str,
                      payload_format: str,
                      payload: str, errored: bool, error_message: dict, exchange_name: str, routing_key: str) -> None:

    if not payload_format:
        payload_format = get_payload_format(payload)

    msg_defaults: dict = {
        "object_identifiers": object_identifiers, "processing_start": processing_start,
        "processing_end": processing_end, "errored": errored, "hash": hash,
        "error_message": json.dumps(error_message), "message_type": message_type, "payload_format": payload_format,
        "payload": payload, "exchange_name": exchange_name, "routing_key": routing_key
    }

    processing_start_date: datetime.datetime = datetime.datetime.fromisoformat(processing_start)
    processing_end_date: datetime.datetime = datetime.datetime.fromisoformat(processing_end)
    processing_seconds: float = (processing_end_date - processing_start_date).total_seconds()

    msg_defaults["processing_time"] = processing_seconds

    with transaction.atomic():
        _ = Message.objects.create(**msg_defaults)

    # Send a new message notification to Websocket with its contents
    # Using async_to_sync because layer.group_send() is an asynchronous method and log_pacer_message() is synchronous
    # According to https://channels.readthedocs.io/en/latest/ "type" should replace the caller underscores [_] for dots [.]

    room_list = [f"{settings.WEBSOCKET_DEFAULT_ROOM_NAME}_room"]
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        f"{settings.WEBSOCKET_DEFAULT_ROOM_NAME}_room",
        {
            "type": "new.message",
            "message": msg_defaults,
        }
    )
