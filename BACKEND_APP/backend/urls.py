from os.path import basename

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.employees.views import EmployeeViewSet
from apps.orders.views import ClientViewSet, OrderViewSet, OrderItemViewSet, PaymentViewSet, ProductionReportView, \
    OrdersReportView
from apps.production.views import ProductViewSet, ProductionBatchViewSet, SubBatchViewSet
from apps.users.views import TelegramVerifyView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'batches', ProductionBatchViewSet, basename='batch')
router.register(r'subbatch', SubBatchViewSet, basename='subbatch')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='order-item')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/verify-telegram/', TelegramVerifyView.as_view(), name='verify-telegram'),
    path('api/reports/production/', ProductionReportView.as_view(), name='production-report'),
    path('api/reports/orders/', OrdersReportView.as_view(), name='orders-report'),
]
