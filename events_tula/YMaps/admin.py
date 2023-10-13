from django.contrib import admin
from .models import *
@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'description', 'start_date', 'end_date', 'address', 'is_registered')
    list_filter = ('is_registered',)
    list_editable = ('is_registered',)

    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return True

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'event', 'is_registered')
    readonly_fields = ('chat_id', 'event', 'is_registered')
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
