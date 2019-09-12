from django.contrib import admin


class AccountAdmin(admin.ModelAdmin):
  list_display = ['id', 'display_user', 'email', 'is_admin', 'token', 'created_at']
  actions = ['make_admin']

  def display_user(self, obj):
    return "%s %s" % (obj.user.first_name, obj.user.last_name)

  def make_admin(self, request, queryset):
    for account in queryset:
      account.is_admin = True
      account.save()
    

  display_user.short_description = 'USER'