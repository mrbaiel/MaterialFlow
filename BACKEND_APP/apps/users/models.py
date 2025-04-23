from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_owner = models.BooleanField(default=False, verbose_name="Является владельцем")
    telegram_id = models.CharField(max_length=64, blank=True, null=True, verbose_name="ID телеграмма")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
