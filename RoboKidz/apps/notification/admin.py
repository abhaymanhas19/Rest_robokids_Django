from django.contrib import admin
from .models import *

# Register your models here.
#admin.site.register(Notification)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['performed_by',
                        'notified_to',
                        'message',
                        'is_read',
                        'performed_at',
                        'message_key',]
    list_filter = ("performed_by",)
    search_fields = ("performed_by",'is_read')