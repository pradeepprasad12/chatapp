from django.urls import re_path

from .consumers import MyASyncConsumer,apiMyASyncConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<user_id>\d+)/(?P<sender_id>\d+)/$', MyASyncConsumer.as_asgi()),
    re_path(r'api/ws/chat/send/$', apiMyASyncConsumer.as_asgi()),

]
