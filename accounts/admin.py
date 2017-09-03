from django.contrib import admin
from .models import Profile
from .models import Option


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user']

admin.site.register(Profile, ProfileAdmin)


class OptionAdmin(admin.ModelAdmin):
    list_display = ['user']

admin.site.register(Option, OptionAdmin)
