from django.contrib import admin
from .models import PurchaseOrder


class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'status', 'vendor', 'quality_rating')
    list_filter = ('status',)
    ordering = ('-created_at',)


admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
