from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^list/$',                         views.AccountReviewsAPIView.as_view(), name='list'),
    url(r'^(?P<id>[0-9a-f-]+)/list/$',      views.AccountReviewsByIdAPIView.as_view(), name='list-by-id'),
    url(r'^(?P<id>[0-9a-f-]+)/create/$',    views.CreateAccountReviewAPIView.as_view(), name='create'),
]