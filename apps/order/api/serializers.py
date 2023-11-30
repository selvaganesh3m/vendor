from rest_framework import serializers
from apps.order.models import PurchaseOrder
from uuid import uuid4

class PurchaseOrderSerializer(serializers.ModelSerializer):
    issue_date = serializers.ReadOnlyField()
    po_number = serializers.ReadOnlyField()
    vendor_name = serializers.ReadOnlyField(source='vendor.name')


    class Meta:
        model = PurchaseOrder
        exclude = ('created_at', 'updated_at')

    def save(self, **kwargs):
        if not self.instance:
            po_number = f'PO{str(uuid4())[:10]}'
            self.validated_data['po_number'] = po_number
        return super().save(**kwargs)
