from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^conversations/$', views.ConversationsAPIView.as_view(), name='conversations'),
]
