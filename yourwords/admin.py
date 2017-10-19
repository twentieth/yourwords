from django.contrib import admin
from .models import English
from .models import Listing
from .models import Contact

class EnglishAdmin(admin.ModelAdmin):
    list_display = ('english', 'polish', 'rating', 'created_at', 'user')
    list_filter = ('rating', 'created_at', 'updated_at', 'user')
    search_fields = ('english', 'polish', 'sentence')
    ordering = ['-created_at', '-updated_at']

admin.site.register(English, EnglishAdmin)


class ListingAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('user',)
    ordering = ['-created_at']

admin.site.register(Listing, ListingAdmin)


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'content', 'cc_myself', 'created_at')
    list_filter = ('email', 'created_at')
    search_fields = ('name', 'email', 'content', 'created_at')
    ordering = ['created_at']
    readonly_fields = ('name', 'email', 'content', 'cc_myself', 'created_at')


admin.site.register(Contact, ContactAdmin)