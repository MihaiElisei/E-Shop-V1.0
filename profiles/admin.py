from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile
from django.utils.html import format_html
# Register your models here.


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'default_town_or_city',
                    'default_county', 'default_country')


admin.site.register(UserProfile, UserProfileAdmin)
