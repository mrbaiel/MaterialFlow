from celery import shared_task
from django.db import models

from apps.orders.models import Order
from apps.production.models import ProductionBatch


@shared_task
def generate_production_report(start_date, end_date):
    pass

@shared_task
def generate_orders_report(status, start_date, end_date):
    pass