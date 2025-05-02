from django.contrib import admin

from apps.employees.models import Employees

@admin.register(Employees)
class EmployeesAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'created_at')
    search_fields = ('first_name', 'last_name')
    ordering = ('first_name',)