from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator



class Employees(models.Model):
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    phone = models.CharField(max_length=14, blank=True, verbose_name="Номер телефона")
    address = models.CharField(max_length=50, blank=True, null=True, verbose_name="Адрес сотрудника")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.first_name


class Salary(models.Model):
    """
    моделька для расчета зп
    хранит начисления по подпартиям, статус, и дату выплаты
    """
    PAYMENT_CHOICES = (
        ("not paid", "Не оплачено"),
        ("paid", "Оплачено")
    )

    employee = models.ForeignKey("employees.Employees", on_delete=models.CASCADE, verbose_name="Сотрудник")
    sub_batch = models.ForeignKey("production.SubBatch", on_delete=models.CASCADE, verbose_name="Подпартия")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Сумма")
    paid_date = models.DateField(verbose_name="Дата выплаты", null=True, blank=True)
    payment_status = models.CharField(choices=PAYMENT_CHOICES, max_length=15, default="not paid", verbose_name="Статус оплаты")
    calculation_date = models.DateField(verbose_name="Дата расчета")
    created_at = models.DateField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Зарплата"
        verbose_name_plural = "Зарплаты"
        indexes = [
            models.Index(fields=["paid_date"]),
            models.Index(fields=["employee", "paid_date"])
        ]

    def __str__(self):
        return f"{self.employee} - {self.amount}сом"

    def clean(self):
        """
         проверка того что сотрудник участвовал в подпартии
        """
        from apps.production.models import SubBatch
        if isinstance(self.sub_batch, SubBatch):
            if self.employee not in self.sub_batch.employees.all():
                raise ValidationError("Работник не участовал в этой подпартии")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)