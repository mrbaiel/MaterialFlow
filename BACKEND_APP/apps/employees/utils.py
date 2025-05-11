import csv
import datetime

from django.http import HttpResponse
from django.db.models import Sum
import logging

logger = logging.getLogger(__name__)


def get_salary_totals(queryset):
    """
    возврощает сумму зарплат по сотрудникам, разделённые на оплаченные и неоплаченные.
    """
    try:
        paid_totals = queryset.filter(payment_status='paid').values('employee__first_name','employee__last_name').annotate(total=Sum('amount')).order_by('-total')
        not_paid_totals = queryset.filter(payment_status='not paid').values('employee__first_name','employee__last_name').annotate(total=Sum('amount')).order_by('-total')
        logger.info(f"Paid totals: {list(paid_totals)}")
        logger.info(f"Not paid totals: {list(not_paid_totals)}")
        return {'paid_total': paid_totals, 'not_paid_total': not_paid_totals}
    except Exception as e:
        logger.error(f"ОШИБКА в get_salary_totals: {str(e)}")
        return {'paid_total': [], 'not_paid_total': []}

def generate_salary_report(queryset):
    """
    генерирует csv-отчёт по зарплатам.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="salary_report_{datetime.datetime.now().strftime("%d.%m.%Y")}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Сотрудник','Дата расчёта','Сумма','Статус','Дата выплаты'])
    for salary in queryset.select_related('employee'):
        writer.writerow([
            f"{salary.employee.first_name} {salary.employee.last_name}",
            salary.calculation_date,
            salary.amount,
            salary.get_payment_status_display(),
            salary.paid_date or ''
        ])
    paid_total = queryset.filter(payment_status='paid').aggregate(total=Sum('amount'))['total'] or 0
    not_paid_total = queryset.filter(payment_status='not paid').aggregate(total=Sum('amount'))['total'] or 0
    writer.writerow([])
    writer.writerow(['Итого оплачено', '', paid_total, '', ''])
    writer.writerow(['Итого не оплачено', '', not_paid_total, '', ''])
    return response