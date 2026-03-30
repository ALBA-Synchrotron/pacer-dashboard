from django.contrib import admin
from django.contrib.auth.models import Group

from dashboard.models import GroupProfile


class GroupProfileInline(admin.StackedInline):
    model = GroupProfile
    can_delete = False

class GroupAdmin(admin.ModelAdmin):
    inlines = [GroupProfileInline]

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)