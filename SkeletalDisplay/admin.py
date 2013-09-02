from django.contrib import admin
import SkeletalDisplay.models as m

class UserSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')

admin.site.register(m.UserSetting, UserSettingAdmin)