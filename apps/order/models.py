from uuid import uuid4

from django.db import models, transaction
from django.db.models import (Avg, Case, Count, ExpressionWrapper, F, fields,
                               Sum, When)
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.core.models import TimestampModel
from apps.metric.models import PerformanceMetric
from apps.vendor.models import Vendor


class PurchaseOrder(TimestampModel):
    ORDER_STATUS_CHOICES = (
        ('PENDING', 'PENDING'),
        ('COMPLETED', 'COMPLETED'),
        ('CANCELLED', 'CANCELLED'),
    )
    po_number = models.CharField(
        max_length=20, unique=True, editable=False, primary_key=True)
    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(
        max_length=30, choices=ORDER_STATUS_CHOICES, default='PENDING')
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField(null=True, blank=True)
    acknowledgement_date = models.DateTimeField(null=True, blank=True)
    delivered_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'vm_purchase_orders'

    def __str__(self) -> str:
        return f'{self.po_number}'


@receiver(pre_save, sender=PurchaseOrder)
@transaction.atomic
def po_pre_save_handler(sender, instance, *args, **kwargs):
    if not instance.po_number:
        instance.po_number = f'PO{str(uuid4())[:10]}'


@receiver(post_save, sender=PurchaseOrder)
@transaction.atomic
def po_post_save_handler(sender, instance, created, *args, **kwargs):
    if not created:
        vendor = instance.vendor

        if vendor and instance.acknowledgement_date and instance.issue_date:
            # On time delivery Rate:
            delivery_rate_aggregation = PurchaseOrder.objects.filter(
                vendor=vendor, status='COMPLETED'
            ).aggregate(
                total_delivered_early=Sum(
                    Case(
                        When(delivered_on__lt=F('delivery_date'), then=1),
                        default=0,
                        output_field=fields.IntegerField(),
                    )
                ),
                total_completed=Count('po_number')
            )

            total_po_delivered_early_count = delivery_rate_aggregation.get(
                'total_delivered_early', 0)
            total_completed_po_count = delivery_rate_aggregation.get(
                'total_completed', 0)
            on_time_delivery_rate = round((
                total_po_delivered_early_count / total_completed_po_count
            ) if total_completed_po_count != 0 else 0, 2)

            # Quality Rating Average
            average_quality_rating = PurchaseOrder.objects.filter(
                vendor=vendor,
                status='COMPLETED',
                quality_rating__isnull=False,
            ).aggregate(avg_quality_rating=Avg('quality_rating'))['avg_quality_rating']

            # Avarage Response Time
            average_acknowledgement_duration = PurchaseOrder.objects.filter(
                vendor=vendor,
                acknowledgement_date__isnull=False,
                issue_date__isnull=False
            ).aggregate(
                avg_acknowledgement_duration=Avg(
                    ExpressionWrapper(
                        F('acknowledgement_date') - F('issue_date'),
                        output_field=fields.DurationField()
                    )
                )
            )['avg_acknowledgement_duration']

            average_acknowledgement_duration_in_min = average_acknowledgement_duration.total_seconds() / 60

            # Fulfillment Rate
            vendor_po_stats = PurchaseOrder.objects.filter(vendor=vendor).aggregate(
                            total_po_count=Count('po_number'),
                            completed_po_count=Count('po_number', filter=models.Q(status='COMPLETED'))
                            )
            total_po_count = vendor_po_stats['total_po_count']          
            completed_po_count = vendor_po_stats['completed_po_count']


            fulfillment_rate = round(completed_po_count / total_po_count if total_po_count != 0 else 0, 2)
            
            # Updating for Vendor
            vendor.on_time_delivery_rate = on_time_delivery_rate
            vendor.quality_rating_avg = 0 if average_quality_rating is None else average_quality_rating
            vendor.avg_response_time = average_acknowledgement_duration_in_min
            vendor.fulfillment_rate = fulfillment_rate
            vendor.save()

            # Creating Performance metricts
            PerformanceMetric.objects.create(
                vendor=vendor,
                on_time_delivery_rate=on_time_delivery_rate,
                quality_rating_avg=0 if average_quality_rating is None else average_quality_rating,
                average_response_time=average_acknowledgement_duration_in_min,
                fulfilment_rate=fulfillment_rate
            )
