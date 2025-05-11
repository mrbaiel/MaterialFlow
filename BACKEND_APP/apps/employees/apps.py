from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.employees"
    verbose_name = "2. Сотрудники"

    def ready(self):
        try:
            import apps.employees.signals
        except ImportError as e:
            print(f"Ошибка импорта {e}")