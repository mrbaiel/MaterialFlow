from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from django.http import FileResponse
from .tasks import generate_production_report, generate_orders_report

from apps.orders.models import Client, Order, OrderItem, Payment
from apps.orders.serializers import ClientSerializer, OrderSerializer, OrderItemSerializer, PaymentSerializer
from apps.employees.views import IsOwnerOrAdmin


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['first_name', 'last_name']
    search_fields = ['first_name', 'last_name']


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('client')
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['status', 'payment_status', 'order_date']
    search_fields = ['client__first_name', 'client__last_name']


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related('order', 'product')
    serializer_class = OrderItemSerializer
    permission_classes = [AllowAny, ]
    filterset_fields = ['order']


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('order')
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny, ]
    filterset_fields = ['payment_date']


class ProductionReportView(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if not (start_date and end_date):
            return Response({'error': 'start_date and end_date required'}, status=400)

        task = generate_production_report.delay(start_date, end_date)
        file_path = task.get()
        return FileResponse(open(file_path, 'rb'), filename='production_report.xlsx')


class OrdersReportView(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request):
        status = request.query_params.get('status')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if not (start_date and end_date):
            return Response({'error': 'start_date and end_date required'}, status=400)

        task = generate_orders_report.delay(status, start_date, end_date)
        file_path = task.get()
        return FileResponse(open(file_path, 'rb'), filename='orders_report.xlsx')
