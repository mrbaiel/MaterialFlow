from django.db import models
from django.core.validators import MinValueValidator

from apps.materials.constants import MATERIAL_TYPES


class Material(models.Model):
    """
    Учет поставок сырья
    """
    name = models.CharField(max_length=50, choices=MATERIAL_TYPES, verbose_name="Тип материала")
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Количество (тонны)"
    )
    delivery_date = models.DateField(verbose_name="Дата поставки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"
        indexes = [
            models.Index(fields=["delivery_date"]),
        ]

    def __str__(self):
        return f"{self.get_name_display()}, ({self.quantity} т)"

