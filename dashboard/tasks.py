import datetime
import asyncio
import datetime
import json
from asyncio import AbstractEventLoop

from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import transaction

from dashboard.models import Message
from dashboard.utils.messages import get_payload_format

_loop: AbstractEventLoop | None = None

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

    # WEBSOCKET NEW MESSAGE EVENT

    # channels-rabbitmq lib driver requires a persistent event loop running before initializing and does not support
    # async_to_sync the way channels-redis does.
    # Since this is executed in a celery synchronous worker, using asyncio.run would create a new eventloop each time a
    # message arrives, which triggers a RuntimeError because the connection is bound to the first event loop it saw.
    # We can solve this by using a singleton-like approach to reuse the same loop across all tasks within the same
    # worker process.
    def get_worker_loop():
        global _loop
        if _loop is None or _loop.is_closed():
            try:
                _loop = asyncio.get_event_loop()
            except RuntimeError:
                _loop = asyncio.new_event_loop()
                asyncio.set_event_loop(_loop)
        return _loop

    async def send_to_channel():
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"{settings.WEBSOCKET_DEFAULT_ROOM_NAME}_room",
            {
                "type": "new.message", # replace the caller underscores [_] for dots [.]
                "message": {"event": "new.message"},
            }
        )

    # Use async_to_sync(send_to_channel()) if using Redis and forget about the loop.
    loop = get_worker_loop()
    loop.run_until_complete(send_to_channel())
