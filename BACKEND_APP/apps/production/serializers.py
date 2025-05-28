from rest_framework import serializers
from django.db import models
from apps.employees.models import Employees
from apps.employees.serializers import EmployeeSerializer
from apps.production.models import Product, ProductionBatch, SubBatch


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'is_colored', 'color_type', 'price_per_unit', 'block_rate']

    def validate(self, data):
        if not data.get('is_colored') and data.get('color_type'):
            raise serializers.ValidationError("Цвет должен отсутствовать или иметь тип краски")
        return data


class ProductionBatchSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, source='product'
    )

    class Meta:
        model = ProductionBatch
        fields = ['id', 'product', 'product_id', 'quantity', 'production_date', 'created_at']
        read_only_fields = ['created_at']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Количество должно быть больше 0")
        return value

class SubBatchSerializer(serializers.ModelSerializer):
    production_batch = serializers.PrimaryKeyRelatedField(queryset=ProductionBatch.objects.all())
    employees = EmployeeSerializer(many=True, read_only=True)
    employee_ids = serializers.PrimaryKeyRelatedField(
        queryset=Employees.objects.all(),
        many=True,
        write_only=True,
        source="employees",
    )

    class Meta:
        model = SubBatch
        fields = ['id', 'production_batch', 'quantity', 'employees', 'employee_ids', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        quantity = data.get('quantity')
        production_batch = data.get('production_batch')
        employee_ids = data.get('employees', [])

        if quantity <= 0:
            raise serializers.ValidationError("Количество должно быть больше 0")
        if not employee_ids:
            raise serializers.ValidationError("Должен быть выбран хотя бы один сотрудник")

        total_subbatch_quantity = SubBatch.objects.filter(
            production_batch=production_batch
        ).exclude(pk=self.instance.pk if self.instance else None).aggregate(
            models.Sum('quantity')
        )['quantity__sum'] or 0

        if total_subbatch_quantity + quantity > production_batch.quantity:
            raise serializers.ValidationError("Общее количество подпартий превышает количество партии")

        return data
