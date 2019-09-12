from django.contrib import admin


class ReviewAdmin(admin.ModelAdmin):
  list_display = [
    'id', 
    'display_reviewer', 
    'display_reviewee', 
    'rating', 
    'created_at'
  ]

  def display_reviewer(self, obj):
    return "%s %s" % (
      obj.reviewer.user.first_name, 
      obj.reviewer.user.last_name
    )
  
  def display_reviewee(self, obj):
    return "%s %s" % (
      obj.reviewee.user.first_name, 
      obj.reviewee.user.last_name
    )

  display_reviewer.short_description = 'REVIEWER'
  display_reviewee.short_description = 'REVIEWEE'

class ChatRoomAdmin(admin.ModelAdmin):
  list_display = [
    'room', 
    'display_first', 
    'display_second', 
    'created_at'
  ]

  def display_first(self, obj):
    return "%s %s" % (
      obj.first.user.first_name, 
      obj.first.user.last_name
    )

  def display_second(self, obj):
    return "%s %s" % (
      obj.second.user.first_name, 
      obj.second.user.last_name
    )

  display_first.short_description = 'ACCOUNT'
  display_second.short_description = 'ACCOUNT'

