from django.contrib import admin

from apps.materials.models import Material

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "quantity", "delivery_date", "created_at")
    list_filter = ("name", "delivery_date")
    search_fields = ("name",)
    date_hierarchy = "delivery_date"
    ordering = ("-delivery_date",)

