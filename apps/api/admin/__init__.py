from django.contrib import admin
from apps.api.models import *

from .post import PostAdmin, PhotosAdmin
from .account import AccountAdmin
from .review import ReviewAdmin, ChatRoomAdmin

admin.site.register(User)
admin.site.register(UserAccount, AccountAdmin)
admin.site.register(UserSavedPosts)
admin.site.register(UserAccountFollowers)

admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(Message)

admin.site.register(Posts, PostAdmin)
admin.site.register(PostPhotos, PhotosAdmin)

admin.site.register(Review, ReviewAdmin)
admin.site.register(Notification)