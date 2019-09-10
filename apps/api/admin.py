from django.contrib import admin
from requests.exceptions import ConnectionError

from .models import *

import os
import requests
# Register your models here.

class PostAdmin(admin.ModelAdmin):
  
  def notify_user(self, token, data):
    try:
      url = os.environ.get('SOCKET_SERVER', 'http://localhost:3000')
      r = requests.post(url + '/notify/' + token + '/', data=data)
    except ConnectionError:
      pass

  def save_model(self, request, obj, form, change):
      obj.user = request.user
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
          

admin.site.register(User)
admin.site.register(UserAccount)
admin.site.register(Posts, PostAdmin)
admin.site.register(PostPhotos)
admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(UserSavedPosts)
admin.site.register(UserAccountFollowers)
admin.site.register(Review)
admin.site.register(Notification)
