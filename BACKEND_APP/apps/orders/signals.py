from Tools.demo.mcast import sender
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import models

from apps.orders.models import OrderItem, Order


@receiver([post_save, post_delete], sender = OrderItem)
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
    total = order.orderitem_set.aggregate(total=models.Sum('price'))['total'] or 0
    Order.objects.filter(pk=order.pk).update(total_price=total)

