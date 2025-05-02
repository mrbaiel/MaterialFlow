from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    модель для пользователей
    хранит: фио, пароль и роль
    """
    ROLE_CHOICES = (
        ('developer', "Разработчик"),
        ('owner', "Владелец"),
        ('admin', 'Админ')
    )
    role = models.CharField(max_length=15,
                            choices=ROLE_CHOICES,
                            default='admin',
                            verbose_name="Роль"
                            )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.first_name