from django.conf.urls import url
from . import consumers

websocket_urlpatterns = [
	url(r'^(?P<token>\w+)/(?P<id>\d+)/$',  consumers.ChatConsumer),
]