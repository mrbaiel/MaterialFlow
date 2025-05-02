from django.db import models
from django.utils import timezone


class Employees(models.Model):
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")
    phone = models.CharField(max_length=14, blank=True, verbose_name="Номер телефона")

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.first_name
