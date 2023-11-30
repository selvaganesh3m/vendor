from django.db import models
from apps.core.models import TimestampModel
from apps.vendor.models import Vendor

class PerformanceMetric(TimestampModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='metrics')
    recorded_at = models.DateTimeField(auto_now_add=True)  # "date" is the reserved keyword in python. So, used recorded_at
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfilment_rate = models.FloatField()

    class Meta:
        db_table = 'vm_performance_metrics'

    def __str__(self) -> str:
        return f'{self.vendor} -> {self.recorded_at.date()}'




