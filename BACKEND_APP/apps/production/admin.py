from django.contrib import admin
from django import forms
from apps.production.models import Product, ProductionBatch, SubBatch


class ProductForm(forms.ModelForm):
    """
    форма которая скрывает color_type если is colored = False
    """
    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.is_colored:
            self.fields['color_type'].widget = forms.HiddenInput()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ('name', 'price_per_unit',"color_type", 'block_rate')
    list_filter = ('is_colored',)
    search_fields = ('name', 'color_type')
    list_editable = ('price_per_unit', 'block_rate')
    fieldsets = (
        (None, {
            'fields': ('name', 'price_per_unit', 'block_rate')
        }),
        ('Характеристики', {
            'fields': ('is_colored', 'color_type')
        }),
    )


@admin.register(ProductionBatch)
class ProductionBatchAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'production_date', 'created_at')
    list_filter = ('product', 'production_date')
    search_fields = ('product__name',)
    date_hierarchy = 'production_date'
    ordering = ('-production_date',)


@admin.register(SubBatch)
class SubBatchAdmin(admin.ModelAdmin):
    list_display = ('production_batch', 'quantity', 'created_at')
    list_filter = ('production_batch__production_date',)
    filter_horizontal = ('employees',)

    def employee_count(self, obj):
        return obj.employees.count()
    employee_count.short_description = "Число сотрудников"

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.save()