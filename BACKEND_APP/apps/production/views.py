from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from rest_framework import viewsets

from apps.employees.views import IsOwnerOrAdmin
from apps.production.models import Product, ProductionBatch, SubBatch
from apps.production.serializers import ProductSerializer, ProductionBatchSerializer, SubBatchSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrAdmin, IsAuthenticated]
    filterset_fields = ['is_colored']
    search_fields = ['name', 'color_type']

class ProductionBatchViewSet(viewsets.ModelViewSet):
    queryset = ProductionBatch.objects.select_related('product')
    serializer_class = ProductionBatchSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filterset_fields = ['production_date']
    search_fields = ['product__name']

class SubBatchViewSet(viewsets.ModelViewSet):
    queryset = SubBatch.objects.select_related('production_batch__product').prefetch_related('employees')
    serializer_class = SubBatchSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filterset_fields = ['production_batch']
