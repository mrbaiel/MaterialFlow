from Tools.demo.mcast import sender
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import models, transaction

from apps.orders.models import OrderItem, Order, Payment


@receiver([post_save, post_delete], sender=OrderItem)
@receiver(post_save, sender=Order)
def update_total_price(sender, instance, **kwargs):
    """
    обновляем total_price в Order при создании/обновлении Order или OrderItem,
    а также при удалении OrderItem
    """
    if sender == OrderItem:
        order = instance.order
    else:
        order = instance
    total_price = order.orderitem_set.aggregate(total=models.Sum('price'))['total'] or 0
    total_quantity = order.orderitem_set.aggregate(total=models.Sum('quantity'))['total'] or 0
    Order.objects.filter(pk=order.pk).update(total_price=total_price, quantity=total_quantity)


@receiver(post_save, sender=Order)
def handle_initial_payment(sender, instance, **kwargs):
    """
    создаем или обновляем платеж для initial_payment при c/u Order
    """
    created = kwargs.get('created', False)
    if instance.initial_payment > 0:
        with transaction.atomic():
            existing_payment = instance.payment_set.filter(payment_data=instance.order_date,
                                                           created_at__gte=instance.created_at).first()

            if created and not existing_payment:
                # Новый заказ, создаём платёж
                Payment.objects.create(
                    order=instance,
                    amount=instance.initial_payment,
                    payment_date=instance.order_date
                )
            elif existing_payment and existing_payment.amount != instance.initial_payment:
                existing_payment.amount = instance.initial_payment
                existing_payment.save()


@receiver([post_save, post_delete], sender=Payment)
def update_payment_status(sender, instance, **kwargs):
    """
    обновляем payment_status в Order и for_payment в Payment при crud
    """
    order = instance.order

    with transaction.atomic():
        total_payments = order.payment_set.aggregate(total=models.Sum('amount'))['total'] or 0
        if total_payments >= order.total_price:
            payment_status = "paid"
        elif total_payments > 0:
            payment_status = "partial"
        else:
            payment_status = "pending"

        Order.objects.filter(pk=order.pk).update(payment_status=payment_status)
