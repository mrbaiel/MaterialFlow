from rest_framework import serializers

from apps.employees.models import Employees


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employees
        fields = ['id', 'first_name', 'last_name', 'phone', 'address']
        read_only_fields = ['created_at']


