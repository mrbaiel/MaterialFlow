from django.contrib import admin

from apps.orders.models import Client, Order, OrderItem, Payment


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'created_at')
    search_fields = ('first_name', 'last_name')
    ordering = ('first_name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'client', 'quantity', 'total_price',
                    'advance_price', 'payment_status', 'order_date'
                    )
    list_filter = ('payment_status', 'status', 'order_date')
    search_fields = ('client__name',)
    date_hierarchy = 'order_date'
    inlines = ['OrderItemInline']

    class OrderItemInline(admin.TabularInline):
        model = OrderItem
        extra = 1


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('product',)
    search_fields = ('order__client__name', 'product__name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'payment_date', 'created_at')
    list_filter = ('payment_date',)
    search_fields = ('order__client__name',)
    date_hierarchy = 'payment_date'
