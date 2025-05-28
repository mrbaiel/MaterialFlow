# from datetime import datetime
# from dateutil.relativedelta import relativedelta
# import pandas as pd
#
# from django.db.models.functions import TruncMonth
# from django.db.models import Sum
#
# from apps.orders.models import Payment, Order, OrderItem
# from apps.production.models import ProductionBatch
#
#
# class AnalyticsManager:
#     """ аналитика и прогнозы"""
#
#     def __init__(self, year=None, month=None):
#         self.year = year
#         self.month = month
#         self.start_date = datetime(year, month, 1) if month and year else None
#         self.end_date = self.start_date + relativedelta(months=1) if self.start_date else None
#
#     def get_filters(self):
#         filters = {}
#         if self.year and self.month:
#             filters["order_date__gte"] = self.start_date
#             filters["order_date__lt"] = self.end_date
#
#         elif self.year:
#             filters["order_date__year"] = self.year
#
#         return filters
#
#     def get_analytics_data(self):
#         filters = self.get_filters()
#
#         # выручка
#         revenue_filters = {}
#         if self.month and self.year:
#             revenue_filters["payment_date__gte"] = self.start_date
#             revenue_filters["payment_date__lt"] = self.end_date
#
#         elif self.year:
#             revenue_filters["payment_date__year"] = self.year
#
#         revenue = Payment.objects.filter(**revenue_filters).aggregate(total=Sum('amount'))['total'] or 0
#         prev_filters = {
#             'payment_date__gte': (self.start_date - relativedelta(months=1)) if self.month and self.year
#             else datetime(self.year - 1, 1, 1) if self.year
#             else datetime.now() - relativedelta(years=1),
#             'payment_date_lt': self.start_date if self.year and self.month else datetime(self.year, 1,
#                                                                                          1) if self.year else datetime.now()
#         }
#         prev_revenue = Payment.objects.filter(**prev_filters).aggregate(total=Sum('amount'))['total'] or 0
#         revenue_change = ((revenue - prev_revenue) / prev_revenue * 100) if prev_revenue else 0
#
#         # объём продаж
#         sales_volume = Order.objects.filter(**filters).aggregate(total=Sum('quantity'))['total'] or 0
#         prev_order_filters = {
#             'order_date__gte': (self.start_date - relativedelta(months=1)) if self.month and self.year else datetime(
#                 self.year - 1, 1, 1) if self.year else datetime.now() - relativedelta(years=1),
#             'order_date__lt': self.start_date if self.month and self.year else datetime(self.year, 1,
#                                                                                         1) if self.year else datetime.now()
#         }
#         prev_sales_volume = Order.objects.filter(**prev_order_filters).aggregate(total=Sum('quantity'))['total'] or 0
#         sales_change = ((sales_volume - prev_sales_volume) / prev_sales_volume * 100) if prev_sales_volume else 0
#
#         # Соотношение произведённого/проданного
#         production_filters = {}
#         if self.month and self.year:
#             production_filters['production_date__gte'] = self.start_date
#             production_filters['production_date__lt'] = self.end_date
#         elif self.year:
#             production_filters['production_date__year'] = self.year
#         produced = ProductionBatch.objects.filter(**production_filters).aggregate(total=Sum('quantity'))['total'] or 0
#         stock_balance = produced - sales_volume
#
#         # Рентабельность (условно: OrderItem.price - Product.price_per_unit)
#         profitability_filters = filters.copy()
#         profitability = OrderItem.objects.filter(**profitability_filters).values('product__name').annotate(
#             total_income=Sum('price'),
#             total_cost=Sum('product__price_per_unit')
#         )
#         profitability = [
#             {
#                 'product': p['product__name'],
#                 'margin': ((p['total_income'] - p['total_cost']) / p['total_income'] * 100) if p['total_income'] else 0
#             }
#             for p in profitability
#         ]
#
#         # Данные для графика (выручка и продажи за 6 месяцев)
#         end_date = datetime.now()
#         start_date = end_date - relativedelta(months=6)
#         revenue_data = Payment.objects.filter(payment_date__gte=start_date, payment_date__lte=end_date) \
#             .annotate(month=TruncMonth('payment_date')) \
#             .values('month').annotate(total=Sum('amount')).order_by('month')
#         sales_data = Order.objects.filter(order_date__gte=start_date, order_date__lte=end_date) \
#             .annotate(month=TruncMonth('order_date')) \
#             .values('month').annotate(total=Sum('quantity')).order_by('month')
#
#         chart_labels = [(start_date + relativedelta(months=i)).strftime('%b %Y') for i in range(6)]
#         chart_revenue = [0] * 6
#         chart_sales = [0] * 6
#         for r in revenue_data:
#             month_idx = (r['month'].year - start_date.year) * 12 + r['month'].month - start_date.month
#             if 0 <= month_idx < 6:
#                 chart_revenue[month_idx] = r['total'] or 0
#         for s in sales_data:
#             month_idx = (s['month'].year - start_date.year) * 12 + s['month'].month - start_date.month
#             if 0 <= month_idx < 6:
#                 chart_sales[month_idx] = s['total'] or 0
#
#         return {
#             'revenue': revenue,
#             'revenue_change': revenue_change,
#             'sales_volume': sales_volume,
#             'sales_change': sales_change,
#             'produced': produced,
#             'stock_balance': stock_balance,
#             'profitability': profitability,
#             'chart_labels': chart_labels,
#             'chart_revenue': chart_revenue,
#             'chart_sales': chart_sales,
#         }
#
#     def get_forecast(self):
#         """Прогноз продаж и производства на следующий месяц."""
#         end_date = datetime.now()
#         start_date = end_date - relativedelta(months=3)
#         payments = Payment.objects.filter(payment_date__gte=start_date, payment_date__lte=end_date) \
#             .values('amount')
#         orders = Order.objects.filter(order_date__gte=start_date, order_date__lte=end_date) \
#             .values('quantity')
#
#         df_payments = pd.DataFrame(payments)
#         df_orders = pd.DataFrame(orders)
#
#         forecast_revenue = df_payments['amount'].mean() if not df_payments.empty else 0
#         forecast_sales = df_orders['quantity'].mean() if not df_orders.empty else 0
#         forecast_production = forecast_sales
#
#         return {
#             'forecast_revenue': round(forecast_revenue, 2),
#             'forecast_sales': round(forecast_sales),
#             'forecast_production': round(forecast_production),
#         }
#
#     def get_risks(self):
#         """Проверка рисков дефицита блоков."""
#         forecast = self.get_forecast()
#         forecast_sales = forecast['forecast_sales']
#         next_month = (datetime.now() + relativedelta(months=1)).strftime('%B %Y')
#         planned_production = forecast['forecast_production']
#         stock_balance = self.get_analytics_data()['stock_balance']
#
#         risks = []
#         if forecast_sales > (planned_production + stock_balance):
#             deficit = forecast_sales - (planned_production + stock_balance)
#             risks.append({
#                 'month': next_month,
#                 'risk': f'Дефицит {int(deficit)} блоков',
#                 'details': f'Прогноз продаж ({int(forecast_sales)}) '
#                            f'превышает производство ({int(planned_production)}) '
#                            f'и остаток ({int(stock_balance)}).'
#             })
#
#         return risks