from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Product(models.Model):
    """
    Модель для видов пескоблока (20ки, 15ки, тумбы...)
    """
    name = models.CharField(max_length=100, verbose_name="Категория")
    is_colored = models.BooleanField(default=False, verbose_name="Цветной")
    color_type = models.CharField(max_length=50, blank=True, verbose_name="Тип цвета")
    block_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Ставка за блок",
    )
    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Цена за БЛОК"
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        color = f"{self.color_type}" if self.is_colored and self.color_type else ""
        return f"{self.name} {color}"


class ProductionBatch(models.Model):
    """
    Модель для учета производства
    хранит тип блока, кол и дату
    """
    product = models.ForeignKey(
        Product,
        on_delete= models.CASCADE,
        verbose_name="Категория"
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество (шт)")
    production_date = models.DateField(verbose_name="Дата производства")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Партия производства",
        verbose_name_plural = "Партии производства"
        indexes = [
            models.Index(
                fields=['production_date']
            )
        ]

    def __str__(self):
        return f"{self.product} - {self.quantity}шт {self.production_date}"


class SubBatch(models.Model):
    """
    Модель для подпартий
    используется для расчета зп - Зарплата: (кол * ставка за штуку) / число_сотрудников)
    """
    production_batch = models.ForeignKey(
        ProductionBatch,
        on_delete=models.CASCADE,
        verbose_name="Партия",
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество (шт)")
    employees = models.ManyToManyField("employees.Employees", verbose_name="Сотрудники")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Подпартия"
        verbose_name_plural = "Подпартии"

    def __str__(self):
        return f"{self.production_batch} ({self.quantity})шт"

    def clean(self):
        """
        Проверяет, что сумма подпартий не превышает партию.
        """
        if self.quantity < 0: raise ValidationError('Количество не может быть отрицательным.')
        if self.production_batch:
            total_subbatch_quantity = SubBatch.objects.filter(production_batch=self.production_batch).exclude(pk=self.pk).aggregate(models.Sum('quantity'))['quantity__sum'] or 0
            if total_subbatch_quantity + self.quantity > self.production_batch.quantity:
                raise ValidationError('Сумма количества подпартий превышает количество партии.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
