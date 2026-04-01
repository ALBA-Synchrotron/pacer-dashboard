from django.urls import re_path

from .utils.consumers import MessagesConsumer

websocket_urlpatterns = [
    re_path(r"ws/(?P<room_name>\w+)/$", MessagesConsumer.as_asgi()),
]