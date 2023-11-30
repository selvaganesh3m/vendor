from django.db import models
from apps.core.models import TimestampModel
from apps.vendor.models import Vendor
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from uuid import uuid4
from django.db.models import F, Avg, ExpressionWrapper, fields, Count, Case, When
from apps.metric.models import PerformanceMetric
from django.db import transaction


class PurchaseOrder(TimestampModel):
    ORDER_STATUS_CHOICES = (
        ('PENDING', 'PENDING'),
        ('COMPLETED', 'COMPLETED'),
        ('CANCELLED', 'CANCELLED'),
    )
    po_number = models.CharField(max_length=20, unique=True, editable=False)
    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField()
    delivery_date = models.DateField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=30, choices=ORDER_STATUS_CHOICES)
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    acknowledgement_date = models.DateTimeField(null=True, blank=True)
    delivered_on = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'vm_purchase_orders'

    def __str__(self) -> str:
        return f'{self.po_number} -> {self.vendor}'


@receiver(pre_save, sender=PurchaseOrder)
@transaction.atomic
def po_pre_save_handler(sender, instance, *args, **kwargs):
    if not instance.po_number:
        instance.po_number = f'PO{str(uuid4())[:10]}'


@receiver(post_save, sender=PurchaseOrder)
@transaction.atomic
def po_post_save_handler(sender, instance, created, *args, **kwargs):
    if created:
        print("Just Created")
    else:
        # On time delivery Rate:
        vendor_po_stats = PurchaseOrder.objects.filter(
            vendor=instance.vendor,
            status='COMPLETED',
        ).aggregate(
            completed_and_delivered_po_count=Count(
                Case(
                    When(delivered_on__lte=F('delivery_date'), then=1),
                    output_field=fields.IntegerField()
                )
            ),
            completed_po_count=Count('id', filter=F('status') == 'COMPLETED')
        )

        completed_and_delivered_po_count = vendor_po_stats['completed_and_delivered_po_count']
        completed_po_count = vendor_po_stats['completed_po_count']

        on_time_delivery_rate = completed_and_delivered_po_count / completed_po_count if completed_po_count != 0 else 0

        # Quality Rating Average
        average_quality_rating = PurchaseOrder.objects.filter(
            vendor=instance.vendor,
            status='COMPLETED',
        ).aggregate(avg_quality_rating=Avg('quality_rating'))['avg_quality_rating']

        # Avarage Response Time
        average_acknowledgement_duration = PurchaseOrder.objects.filter(
            vendor=instance.vendor,
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
        vendor_po_stats = PurchaseOrder.objects.filter(vendor=instance.vendor).aggregate(
            total_po_count=Count('id'),
            completed_po_count=Count('id', filter=F('status') == 'COMPLETED')
        )

        total_po_count = vendor_po_stats['total_po_count']
        completed_po_count = vendor_po_stats['completed_po_count']

        fulfillment_rate = completed_po_count / \
            total_po_count if total_po_count != 0 else 0
        vendor = instance.vendor

        # Updating in vendor's profile
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
