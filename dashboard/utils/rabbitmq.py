import json
import logging

from django.conf import settings
from pika import PlainCredentials, ConnectionParameters, BlockingConnection, BasicProperties
from pika.exceptions import UnroutableError

logger = logging.getLogger(__name__)


class GenericPublisher:

    @classmethod
    def __get_broker_connection(cls) -> BlockingConnection or None:
        host: str = settings.PACER_RMQ_HOST
        port: int = settings.PACER_RMQ_PORT
        username: str = settings.PACER_RMQ_USERNAME
        password: str = settings.PACER_RMQ_PASSWORD
        vhost: str = settings.PACER_RMQ_VIRTUAL_HOST

        if not host: return None

        credentials: PlainCredentials or None = None
        if username and settings.PACER_RMQ_PASSWORD:
            credentials: PlainCredentials = PlainCredentials(username, password)

        params: ConnectionParameters = ConnectionParameters(
            host=settings.PACER_RMQ_HOST,
            **({"credentials": credentials} if credentials is not None else {}),
            **({"port": port} if port != 0 else {}),
            **({"virtual_host": vhost} if vhost is not None else {"virtual_host": "/"})
        )

        return BlockingConnection(params)

    @classmethod
    def send_messages_to_broker(cls, messages: list, exchange_name: str, routing_key: str = None,
                                  headers: dict = None):
        broker_conn: BlockingConnection or None = cls.__get_broker_connection()
        properties: BasicProperties = BasicProperties(headers=headers) if headers else None
        if not broker_conn: return

        with broker_conn.channel() as channel:
            channel.confirm_delivery()
            for message in messages:
                logger.debug(f"Sending message to broker: {message}")
                try:
                    channel.basic_publish(
                        exchange=exchange_name,
                        routing_key=routing_key,
                        body=json.dumps(message, ensure_ascii=False),
                        properties=properties)
                    logger.debug(f"Message confirmed by broker")
                except UnroutableError as e:
                    logger.error(f"Message NOT sent to broker: {e}")

        broker_conn.close()
