from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<id>\d+)/name/$', views.ChatRoomAPIView.as_view(), name='get-room-name'),
    url(r'^conversations/$', views.ConversationsAPIView.as_view(), name='conversations'),
    url(r'^messages/(?P<id>\d+)/$', views.MessagesAPIView.as_view(), name='messages'),
    url(r'^(?P<room>\w+)/save-message/$', views.SaveMessageAPIView.as_view(), name='save-message'),
]
