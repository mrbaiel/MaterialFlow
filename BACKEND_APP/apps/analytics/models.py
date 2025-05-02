from black.brackets import max_delimiter_priority_in_atom
from django.db import models

from apps.users.models import User

class History(models.Model):
    """
    модель для логирования изменений в сист
    хранит: тип сущности, ID, действие, пользователя и детали изменений
    """
    ACTION_CHOICES = (
        ('create', 'Создания'),
        ('update', 'Редактирование'),
        ('delete', "Удаление"),
    )

    entity_type = models.CharField(max_length=100, verbose_name="Тип сущности")
    entity_id = models.PositiveIntegerField(verbose_name="ID сущности")
    action = models.CharField(max_length=15, choices=ACTION_CHOICES, verbose_name="Действие")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")
    changes = models.JSONField(default=dict, verbose_name="Детали изменений")

    class Meta:
        verbose_name = "История изменений"
        verbose_name_plural = "Истории изменений"
        indexes = [
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.action} {self.entity_type} #{self.entity_id} ({self.timestamp})"
