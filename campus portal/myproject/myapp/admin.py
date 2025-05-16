# myapp/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Timetable, Notification, Comment, MaintenanceRequest
from .models import Announcement, AnnouncementComment
from .models import ClassSchedule
from .models import ServiceBooking


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Timetable)
admin.site.register(Notification)
admin.site.register(Comment)
admin.site.register(MaintenanceRequest)
admin.site.register(Announcement)
admin.site.register(AnnouncementComment)
admin.site.register(ClassSchedule)
admin.site.register(ServiceBooking)