from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^list/$',                 views.PostListAPIView.as_view(), name='list'),
    url(r'^create/$',               views.CreatePostAPIView.as_view(), name='create'),
    url(r'^(?P<id>\d+)/$',          views.PostByIdAPIView.as_view(), name='post-by-id'),
    url(r'^(?P<id>\d+)/edit/$',     views.EditPostByIdAPIView.as_view(), name='edit-post'),
    url(r'^(?P<id>\d+)/save/$',     views.SavePostByIdAPIView.as_view(), name='save-post'),
    url(r'^(?P<id>\d+)/delete/$',   views.DeletePostByIdAPIView.as_view(), name='delete-post'),
    url(r'^(?P<id>\d+)/sold/$',     views.SoldPostByIdAPIView.as_view(), name='sold-post'),
]
