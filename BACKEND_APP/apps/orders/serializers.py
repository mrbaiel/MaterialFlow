from datetime import date

from django.db.models import Sum
from rest_framework import serializers

from apps.orders.models import Client, Order, OrderItem, Payment
from apps.production.models import Product
from apps.production.serializers import ProductSerializer


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'address', 'phone']
        read_only_fields = ['created_at']


class OrderSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        write_only=True,
        source='client',
    )

    class Meta:
        model = Order
        fields = ['id', 'client', 'client_id', 'quantity', 'total_price',
                  'initial_payment', 'payment_status', 'order_date', 'status'
                  ]
        read_only_fields = ['created_at', 'quantity', 'total_price', 'payment_status', ]

    def validate(self, data):
        initial_payment = data.get('initial_payment', 0)
        order_date = data.get('order_date')

        if initial_payment < 0:
            raise serializers.ValidationError("Первоначальный взнос не может быть отрицательным")
        if order_date > date.today():
            raise serializers.ValidationError("Заказ не может быть создан в будущем")
        return data


class OrderItemSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, source='product'
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_id', 'quantity', 'price']
        read_only_fields = ['price']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Количество должно быть больше 0")
        return value


class PaymentSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'payment_date', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        amount = data.get('amount')
        order = data.get('order')
        payment_date = data.get('payment_date')

        if amount <= 0:
            raise serializers.ValidationError("Сумма должна быть больше, чем 0")
        if payment_date > date.today():
            raise serializers.ValidationError("Дата платежа не может быть назначена в будущем")

        existing_payments = order.payment_set.exclude(
            pk=self.instance.pk if self.instance else None
        ).aggregate(total=Sum('amount'))['total'] or 0
        remaining = order.total_price - existing_payments
        if amount > remaining:
            raise serializers.ValidationError(f"Сумма - {amount} превышает остаток {remaining}")

        return data
