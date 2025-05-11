from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.materials.models import Material

@admin.register(Material)
class MaterialAdmin(ModelAdmin):
    list_display = ("name", "quantity", "delivery_date", "created_at")
    list_filter = ("name", "delivery_date")
    search_fields = ("name",)
    date_hierarchy = "delivery_date"
    ordering = ("-delivery_date",)

