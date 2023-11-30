from apps.vendor.models import Vendor
from rest_framework import serializers
from uuid import uuid4


class VendorSerializer(serializers.ModelSerializer):
    vendor_code = serializers.ReadOnlyField()
    class Meta:
        model = Vendor
        exclude = ('created_at', 'updated_at')
    
    def save(self, **kwargs):
        if not self.instance:
            vendor_code = f'VENDOR{str(uuid4())[:10]}'
            self.validated_data['vendor_code'] = vendor_code

        return super().save(**kwargs)
        


