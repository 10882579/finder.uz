from django.contrib import admin
from requests.exceptions import ConnectionError

from apps.api.models import Posts, PostPhotos, Notification

import os
import requests

class PostAdmin(admin.ModelAdmin):
  list_display = ['id', 'display_owner', 'title', 'posted', 'created_at']
  actions = ['delete_query', 'posted']

  def display_owner(self, obj):
    return "%s %s" % (
      obj.account.user.first_name, 
      obj.account.user.last_name,
    )

  def posted(self, request, queryset):
    for post in queryset:
      post.posted = True
      post.save()
  
  def notify_user(self, token, data):
    try:
      url = os.environ.get('SOCKET_SERVER', 'http://localhost:3000')
      r = requests.post(url + '/notify/' + token + '/', data=data)
    except ConnectionError:
      pass

  def save_model(self, request, obj, form, change):
    super().save_model(request, obj, form, change)

    if obj.posted:
      token = obj.account.token

      notif = Notification.objects.create(
        account = obj.account,
        title = "E'lon muvaffaqiyatli chop etildi",
        message = "Hurmatli mijoz,\n\nSizning \"{}\" nomli e'loningiz shop etildi.\n\nHurmat bilan Administratsiya".format(obj.title)
      )

      self.notify_user(token, {
        "type": "notification",
        "id": notif.id,
        "read": notif.read,
        "title": notif.title,
        "message": notif.message,
        "created_at": notif.created_at.timestamp() * 1000
      })

  def delete_query(self, request, queryset):
    for obj in queryset:
      post_photos = PostPhotos.objects.filter(
        post = obj.id
      )
      for photo in post_photos:
        photo.delete()
      obj.delete()
  
  def delete_model(self, request, obj):
    post_photos = PostPhotos.objects.filter(
      post = obj.id
    )
    for photo in post_photos:
      photo.delete()
    obj.delete()
  
  posted.short_description = 'Make available'
  delete_query.short_description = 'Delete posts'
  display_owner.short_description = 'POSTED BY'


class PhotosAdmin(admin.ModelAdmin):
  list_display = ['id', 'display_post', 'display_link', 'created_at']

  def display_link(self, obj):
    return obj.image.url

  def display_post(self, obj):
    return obj.post.title

  display_link.short_description = 'LINK'
  display_post.short_description = 'POST'

