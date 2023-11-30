from django.contrib import admin
from .models import PerformanceMetric



class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'on_time_delivery_rate', 'quality_rating_avg', 'average_response_time', 'fulfilment_rate')

admin.site.register(PerformanceMetric, PerformanceMetricAdmin)
