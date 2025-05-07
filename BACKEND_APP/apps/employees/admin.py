import csv
import logging
from datetime import datetime

from django.http import HttpResponse

from django.contrib import admin
from django.db.models import Sum
from apps.employees.models import Employees, Salary

logger = logging.getLogger(__name__)


@admin.register(Employees)
class EmployeesAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'created_at')
    search_fields = ('first_name', 'last_name')
    ordering = ('first_name',)

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'amount', 'calculation_date', 'payment_status', 'paid_date')
    list_filter = ('employee', 'calculation_date', 'payment_status')
    search_fields = ('employee__first_name', 'employee__last_name')
    list_per_page = 30
    date_hierarchy = 'calculation_date'
    actions = ['export_salary_report']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('employee', 'sub_batch')
        return queryset

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        try:
            queryset = self.get_queryset(request)
            paid_total = queryset.filter(payment_status='paid').values('employee__first_name', 'employee__last_name').annotate(total=Sum('amount')).order_by('-total')
            not_paid_total = queryset.filter(payment_status='not paid').values('employee__first_name', 'employee__last_name').annotate(total=Sum('amount')).order_by('-total')
            logger.info(f"Paid totals: {list(paid_total)}")
            logger.info(f"Not paid totals: {list(not_paid_total)}")
            extra_context['paid_total'] = paid_total
            extra_context['not_paid_total'] = not_paid_total
        except Exception as e:
            logger.error(f"Ошибка в change_view {e}")
        return super().changelist_view(request, extra_context=extra_context)

    def export_salary_report(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="Отчет_зарплат_{datetime.now().strftime("%Y%m%d")}.csv"'
        writer = csv.writer(response)
        writer.writerow(["Сотрудник", "Дата расчета", "Сумма", "Статус", "Дата выплаты"])

        for salary in queryset.select_related('employee'):
            writer.writerow([
                f"{salary.employee.first_name} {salary.employee.last_name}",
                salary.calculation_date,
                salary.amount,
                salary.get_payment_status_display(),
                salary.paid_date or "",
            ])

        paid_total = queryset.filter(payment_status='paid').aggregate(total=Sum('amount'))['total'] or 0
        not_paid_total = queryset.filter(payment_status='not paid').aggregate(total=Sum('amount'))['total'] or 0
        writer.writerow([])
        writer.writerow(['Итого оплачено','', paid_total, '', ''])
        writer.writerow(['Итого не оплачено', '', not_paid_total, '', ''])
        return response
    export_salary_report.short_description = "Экспортировать отчёт по зарплате"
