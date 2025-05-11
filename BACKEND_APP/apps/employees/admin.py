import logging

from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.employees.models import Employees, Salary
from apps.employees.utils import generate_salary_report, get_salary_totals

logger = logging.getLogger(__name__)


@admin.register(Employees)
class EmployeesAdmin(ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'created_at')
    search_fields = ('first_name', 'last_name')
    ordering = ('first_name',)

@admin.register(Salary)
class SalaryAdmin(ModelAdmin):
    list_display = ('employee', 'amount', 'calculation_date', 'payment_status', 'paid_date')
    list_filter = ('employee', 'calculation_date', 'payment_status')
    search_fields = ('employee__first_name', 'employee__last_name')
    list_per_page = 15
    date_hierarchy = 'calculation_date'
    actions = ['export_salary_report', "mark_as_test"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('employee', 'sub_batch')
        return queryset

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        queryset = self.get_queryset(request)
        totals = get_salary_totals(queryset)
        extra_context.update(totals)
        return super().changelist_view(request, extra_context=extra_context)

    def export_salary_report(self, request, queryset):
        return generate_salary_report(queryset)
    export_salary_report.short_description = "Экспортировать отчёт по зарплате"
