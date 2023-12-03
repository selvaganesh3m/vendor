from django.contrib import admin
from .models import Vendor
from apps.order.models import PurchaseOrder



class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendor_code', 'name', 'on_time_delivery_rate', 'quality_rating_avg', 'avg_response_time', 'fulfillment_rate', 'total_orders', 'total_completed_orders')
     
    def total_orders(self, obj):
        return PurchaseOrder.objects.filter(vendor=obj).count()
    total_orders.short_description = 'TOTAL ORDERS'
     
    def total_completed_orders(self, obj):
        return PurchaseOrder.objects.filter(vendor=obj, status='COMPLETED').count()
    total_orders.short_description = 'TOTAL ORDERS COMPLETED'

admin.site.register(Vendor, VendorAdmin)
