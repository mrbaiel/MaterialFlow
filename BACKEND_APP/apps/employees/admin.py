from django.contrib import admin

from apps.employees.models import Employees, Salary


@admin.register(Employees)
class EmployeesAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'created_at')
    search_fields = ('first_name', 'last_name')
    ordering = ('first_name',)

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = (
        'employee', 'sub_batch', 'amount',
        'calculation_date', 'payment_status', 'paid_date'
    )
    list_filter = ('payment_status', 'calculation_date', 'employee')
    search_fields = ('employee__name', 'sub_batch__production_batch__product__name')
    date_hierarchy = 'calculation_date'
    list_editable = ('payment_status', 'paid_date')