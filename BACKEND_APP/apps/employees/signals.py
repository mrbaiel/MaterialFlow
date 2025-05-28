from datetime import date

from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_save

from apps.employees.models import Salary
from apps.production.models import SubBatch

import logging

logger = logging.getLogger(__name__)


@receiver(m2m_changed, sender = SubBatch.employees.through)
def create_salary_records(sender, instance, action, **kwargs):
    """
    сигнал для создания записи Salary для каждого сотрудника при сохранении SubBatch
    """
    if action == "post_add":
        employees = instance.employees.all()
        if not employees:
            return
        existing_salaries = Salary.objects.filter(sub_batch=instance).count()
        if existing_salaries == 0:
            amount = (instance.quantity * instance.production_batch.product.block_rate) / len(employees)
            amount = round(amount, 2)
            for employee in employees:
                Salary.objects.create(
                    employee=employee,
                    sub_batch=instance,
                    amount=amount,
                    calculation_date=instance.production_batch.production_date,
                )
        else:
            logger.info("Записи Salary уже существуют, пропускаем")

@receiver(post_save, sender=Salary)
def update_paid_date(sender, instance, created, **kwargs):
    """
    сигнал для установки текущей даты при изменении статуса оплаты зп сотруднику
    """
    if instance.payment_status == 'paid' and instance.paid_date is None:
        instance.paid_date = date.today()
        instance.save()
        logger.info(f"Дата выплаты для {instance.employee.first_name} - {instance.paid_date}")
