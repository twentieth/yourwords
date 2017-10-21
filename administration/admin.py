from django.contrib import admin
from .models import Log


class LogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'created_at')
    list_filter = ('user', 'action', 'created_at')
    search_fields = ('user',)
    readonly_fields = ('user', 'action', 'created_at')


admin.site.register(Log, LogAdmin)