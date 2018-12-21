from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',                                      views.UserAccountAPIView.as_view(), name='profile'),
    url(r'^login/$',                                views.UserLoginAPIView.as_view(), name='login'),
    url(r'^register/$',                             views.UserRegistrationAPIView.as_view(), name='register'),
    url(r'^update/$',                               views.UserAccountUpdateAPIView.as_view(), name='account-update'),
    url(r'^(?P<id>\d+)/$',                          views.UserAccountByIdAPIView.as_view(), name='account-by-id'),
    url(r'^(?P<id>\d+)/follow/$',                   views.UserAccountFollowAPIView.as_view(), name='account-follow'),
    url(r'^following/page=(?P<page>\d+)$',          views.UserAccountFollowingsAPIView.as_view(), name='account-followings'),
    url(r'^(?P<id>\d+)/posts/page=(?P<page>\d+)$',  views.UserPostListAPIView.as_view(), name='user-posts'),
    url(r'^posts/page=(?P<page>\d+)$',              views.UserSavedPostListAPIView.as_view(), name='user-saved-posts'),
]
