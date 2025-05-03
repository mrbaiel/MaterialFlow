from django.dispatch import receiver
from django.db.models.signals import post_save

from apps.employees.models import Salary
from apps.production.models import SubBatch

#TODO debug signal
@receiver(post_save, sender = SubBatch)
def create_salary_records(sender, instance, created, **kwargs):
    """
    сигнал для создания записи Salary для каждого сотрудника при сохранении SubBatch
    """
    if created:
        employees = instance.employees.all()
        if employees:
            amount = (instance.quantity * instance.production_batch.product.block_rate) / len(employees)
            for employee in employees:
                Salary.objects.create(
                    employee=employee,
                    sub_batch = instance,
                    amount = amount,
                    calculation_date = instance.production_batch.production_date,
                )