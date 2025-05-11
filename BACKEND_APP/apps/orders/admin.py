from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.orders.models import Client, Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('product', 'quantity', 'price')
    readonly_fields = ('price',)


@admin.register(Client)
class ClientAdmin(ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'created_at')
    search_fields = ('first_name', 'last_name')
    ordering = ('first_name',)
    list_per_page = 30

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ( 'id', 'client', 'quantity', 'total_price',
                    'advance_payment', 'payment_status', 'order_date'
                    )
    list_filter = ('payment_status', 'status', 'order_date')
    search_fields = ('client__first_name','client__last_name')
    date_hierarchy = 'order_date'
    inlines = [OrderItemInline]
    readonly_fields = ('total_price',)
    fields = ('client', 'quantity', 'advance_payment', 'payment_status', 'order_date', 'status', 'total_price')


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('product',)
    search_fields = ('order__client__name', 'product__name')


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ('order', 'amount', 'payment_date', 'created_at')
    list_filter = ('payment_date',)
    search_fields = ('order__client__name',)
    date_hierarchy = 'payment_date'
