from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from apps.employees.models import Employees
from apps.employees.serializers import EmployeeSerializer


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        roles = ['owner', 'admin', 'developer']
        return request.user.is_authenticated and request.user.role in roles


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employees.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['first_name', 'last_name']
    search_fields = ['first_name', 'last_name']

