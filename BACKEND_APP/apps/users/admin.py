from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.users.models import User


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ('username', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('username',)
    list_editable = ('role', 'is_active')