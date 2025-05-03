from django.db import models
from django.core.validators import MinValueValidator
# from django.core.exceptions import ValidationError

from apps.orders.constants import PAYMENT_STATUS_CHOICES, ORDER_STATUS_CHOICES
from apps.production.models import Product


class Client(models.Model):
    """
    модель для учета клиентов
    """
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    address = models.TextField(blank=True, verbose_name="Адрес")
    phone = models.CharField(max_length=14, blank=True, verbose_name="Номер телефона")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.first_name


class Order(models.Model):
    """
    модель для учета заказов
    хранит клиента, общее кол, стоимость, аванс, статусы заказа и оплаты
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    quantity = models.PositiveIntegerField(verbose_name="Общее количество")
    total_price = models.DecimalField(max_digits=12,
                                      decimal_places=2,
                                      validators=[MinValueValidator(0)],
                                      verbose_name="Общая стоимость"
                                      )
    advance_payment = models.DecimalField(max_digits=12,
                                          decimal_places=2,
                                          validators=[MinValueValidator(0)],
                                          default=0,
                                          verbose_name="Аванс"
                                          )
    payment_status = models.CharField(max_length=20,
                                      choices=PAYMENT_STATUS_CHOICES,
                                      default="pending",
                                      verbose_name="Статус оплаты"
                                      )
    order_date = models.DateField(verbose_name="Дата заказа")
    status = models.CharField(max_length=10,
                              choices=ORDER_STATUS_CHOICES,
                              default="pending",
                              verbose_name="Статус заказа"
                              )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        indexes = [
            models.Index(fields=['order_date']),
        ]

    def __str__(self):
        return f"Заказ {self.id} ({self.client}, {self.order_date})"

    # def clean(self):
    #     """
    #     Проверяет, что аванс не превышает общей стоимости.
    #     Проверяет, что quantity равно сумме OrderItem.quantity.
    #     """
    #     if self.advance_payment > self.total_price:
    #         raise ValidationError('Аванс не может превышать общую стоимость.')
    #     items_quantity = self.orderitem_set.aggregate(
    #         models.Sum('quantity')
    #     )['quantity__sum'] or 0
    #     if items_quantity != self.quantity:
    #         raise ValidationError(
    #             'Общее количество заказа не равно сумме позиций.'
    #         )
    # def save(self, *args, **kwargs):
    #     self.full_clean()
    #     super().save(*args, **kwargs)
    #

class OrderItem(models.Model):
    """
    модель для позиций заказа
    хранит : заказ, продукт, кол и стоимость
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")
    quantity = models.PositiveIntegerField(verbose_name="Количество (шт)")
    price = models.DecimalField(max_digits=12,
                                decimal_places=2,
                                validators=[MinValueValidator(0)],
                                verbose_name="Стоимость",
                                )
    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product} ({self.quantity})шт"

    def save(self, *args, **kwargs):
        """
        расчитываем price как кол * стоимость одной штуки
        """
        self.price = self.quantity * self.product.price_per_unit
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    моедль для учета платежей (аванс и окончательый платеж)
    хранит: сумму, дату платежа и дату создания
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    amount = models.DecimalField(max_digits=12,
                                 decimal_places=2,
                                 validators=[MinValueValidator(0)],
                                 verbose_name="Сумма платежа",
                                 )
    payment_date = models.DateField(verbose_name="Дата платежа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        indexes = [
            models.Index(fields=['payment_date']),
        ]

    def __str__(self):
        return f"Платеж {self.amount} для {self.order}"
