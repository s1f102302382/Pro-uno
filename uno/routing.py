from django.urls import re_path
#from uno.consumers import UNOConsumer
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/uno/room_index/(?P<room_name>\w+)/$", consumers.UNOConsumer.as_asgi()),
]