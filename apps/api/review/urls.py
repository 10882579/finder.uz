from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^list/$', views.AccountReviewsAPIView.as_view(), name='list'),
]