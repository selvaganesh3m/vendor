import json
import pytz

from django.utils import timezone
from rest_framework import serializers

from apps.order.models import PurchaseOrder
from apps.vendor.models import Vendor
from django.core.validators import MinValueValidator, MaxValueValidator
from vm.settings import TIME_ZONE


class PurchaseOrderSerializer(serializers.ModelSerializer):
    issue_date = serializers.ReadOnlyField()
    po_number = serializers.ReadOnlyField()
    vendor_name = serializers.ReadOnlyField(source='vendor.name')


    class Meta:
        model = PurchaseOrder
        exclude = ('created_at', 'updated_at')


class CreatePurchaseOrderSerializer(serializers.Serializer):
    delivery_date = serializers.DateTimeField()
    items = serializers.JSONField()
    quantity = serializers.IntegerField()

    def validate_delivery_date(self, value):
        current_date = timezone.now()
        if value < current_date:
            raise serializers.ValidationError("Delivery date cannot be in the past.")
        return value
    
    def validate_items(self, value):
        try:
            if isinstance(value, list):
                value = json.dumps(value)

            items_list = json.loads(value)
            if not isinstance(items_list, list):
                raise serializers.ValidationError("Items must be a JSON array.")
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format for items.")
        return value
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        return value
    
    def create(self, validated_data):
        return PurchaseOrder.objects.create(**validated_data)
    

class UpdatePurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = ('vendor', 'delivery_date', 'items', 'quantity')

    def validate_delivery_date(self, value):
        current_date = timezone.now()
        if value < current_date:
            raise serializers.ValidationError("Delivery date cannot be in the past.")
        return value
    
    def validate_items(self, value):
        try:
            if isinstance(value, list):
                value = json.dumps(value)

            items_list = json.loads(value)
            if not isinstance(items_list, list):
                raise serializers.ValidationError("Items must be a JSON array.")
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format for items.")
        return value
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        return value
    
class AddRatingForOrderSerilaizer(serializers.Serializer):
    rating = serializers.IntegerField(validators=[
        MinValueValidator(1, message="Value must be at least 1."),
        MaxValueValidator(5, message="Value must be at most 5.")
    ])

    def save(self, purchase_order: PurchaseOrder, **kwargs):
        rating = self.validated_data['rating']
        purchase_order.quality_rating = rating
        purchase_order.save()
        return purchase_order
        
