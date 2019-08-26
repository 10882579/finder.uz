from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(User)
admin.site.register(UserAccount)
admin.site.register(Posts)
admin.site.register(PostPhotos)
admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(UserSavedPosts)
admin.site.register(UserAccountFollowers)
admin.site.register(Review)
