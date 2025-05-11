from django.contrib import admin

from apps.analytics.models import History


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('entity_type', 'entity_id', 'action', 'user', 'timestamp')
    list_filter = ('entity_type', 'action', 'user', 'timestamp')
    search_fields = ('entity_type',)
    date_hierarchy = 'timestamp'
    readonly_fields = ('changes',)