from apps.vendor.models import Vendor
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class VendorSerializer(serializers.ModelSerializer):
    vendor_code = serializers.ReadOnlyField()
    class Meta:
        model = Vendor
        exclude = ('created_at', 'updated_at', 'user')
    

class CreateVendorSerializer(serializers.Serializer):
    user_email = serializers.EmailField()
    name = serializers.CharField(max_length=125)
    contact_detail = serializers.CharField()
    address = serializers.CharField()

    def validate_user_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email already associated with user.')
        return value
    
    def validate_name(self, value):
        if not value.replace(" ", "").isalpha():
            raise serializers.ValidationError("Name should only contain letters and spaces.")
        return value
    
    def create(self, validated_data):
        user_email = validated_data['user_email']
        name = validated_data['name']
        contact_detail = validated_data['contact_detail']
        address = validated_data['address']

        # user = User.objects.create(email=user_email)
        user = User.objects.create_user(email=user_email, password='samsam')
        vendor = Vendor.objects.create(user=user, name=name, contact_detail=contact_detail, address=address)

        return vendor

class UpdateVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ('name', 'contact_detail', 'address')
        read_only_fields = ('user', 'vendor_code', 'on_time_delivery_rate', 'on_time_delivery_rate', 'avg_response_time', 'fulfillment_rate')
    
    def validate_name(self, value):
        if not value.replace(" ", "").isalpha():
            raise serializers.ValidationError("Name should only contain letters and spaces.")
        return value

class VendorPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ('vendor_code', 'name', 'on_time_delivery_rate', 'on_time_delivery_rate', 'avg_response_time', 'fulfillment_rate')
    


        


