from django.contrib import admin
from .models import Log


class LogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip', 'created_at')
    list_filter = ('user', 'action', 'ip', 'created_at')
    search_fields = ('user', 'action', 'ip')
    readonly_fields = ('user', 'action', 'ip', 'created_at')


admin.site.register(Log, LogAdmin)