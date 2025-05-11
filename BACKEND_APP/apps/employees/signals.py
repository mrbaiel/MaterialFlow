from datetime import date

from django.dispatch import receiver
from django.db.models.signals import post_save

from apps.employees.models import Salary
from apps.production.models import SubBatch

import logging

logger = logging.getLogger(__name__)

#TODO debug signal
@receiver(post_save, sender = SubBatch)
def create_salary_records(sender, instance, created, **kwargs):
    """
    сигнал для создания записи Salary для каждого сотрудника при сохранении SubBatch
    """
    logger.info(f"Сигнал post_save для SubBatch #{instance.id}, created={created}")
    employees = instance.employees.all()
    logger.info(f"Найдено сотрудников: {len(employees)}")
    if employees:
        try:
            existing_salaries = Salary.objects.filter(sub_batch=instance).count()
            if existing_salaries == 0:
                amount = (instance.quantity * instance.production_batch.product.block_rate) / len(employees)
                amount = round(amount,2)

                logger.info(f"Рассчитана зарплата: {amount} сом на сотрудника")
                for employee in employees:
                    Salary.objects.create(
                        employee=employee,
                        sub_batch=instance,
                        amount=amount,
                        calculation_date=instance.production_batch.production_date,
                    )
                    logger.info(f"Создана запись Salary для {employee} - {amount}сом")
            else:
                logger.info("Записи Salary уже существуют, пропускаем")
        except Exception as e:
            logger.error(f"Ошибка при создании Salary: {str(e)}")
    else:
        logger.warning("Нет сотрудников в подпартии, записи Salary не созданы")

@receiver(post_save, sender=Salary)
def update_paid_date(sender, instance, created, **kwargs):
    """
    сигнал для установки текущей даты при изменении статуса оплаты зп сотруднику
    """
    if instance.payment_status == 'paid' and instance.paid_date is None:
        instance.paid_date = date.today()
        instance.save()
        logger.info(f"Дата выплаты для {instance.employee.first_name} - {instance.paid_date}")
