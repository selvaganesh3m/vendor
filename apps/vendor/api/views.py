from apps.vendor.models import Vendor
from .serializers import VendorSerializer, CreateVendorSerializer, UpdateVendorSerializer, VendorPerformanceSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction


class ListCreateVendorAPIView(APIView):

    def get(self, request, *args, **kwargs):
        vendors = Vendor.objects.all()
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = CreateVendorSerializer(data=request.data)
        if serializer.is_valid():
            vendor = serializer.save()
            return Response({'message': 'Vendor created successfully', "vendor_code": vendor.vendor_code}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorRetrieveUpdateDestroyAPIView(APIView):

    def get_vendor(self, vendor_code):
        try:
            vendor = Vendor.objects.get(pk=vendor_code)
        except Vendor.DoesNotExist:
            return None
        return vendor

    def get(self, request, vendor_code, *args, **kwargs):
        vendor = self.get_vendor(vendor_code)
        if not vendor:
            return Response({'message': 'Vendor not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = VendorSerializer(vendor)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, vendor_code, *args, **kwargs):
        vendor = self.get_vendor(vendor_code)
        if not vendor:
            return Response({'message': 'Vendor not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UpdateVendorSerializer(
            vendor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def delete(self, request, vendor_code, *args, **kwargs):
        vendor = self.get_vendor(vendor_code)
        if not vendor:
            return Response({'message': 'Vendor not found.'}, status=status.HTTP_404_NOT_FOUND)
        user = vendor.user
        vendor.delete()
        user.delete()
        return Response({'message': 'Vendor deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    

class VendorPerformansAPIView(APIView):

    def get(self, request, vendor_code, *args, **kwargs):
        try:
            vendor = Vendor.objects.get(vendor_code=vendor_code)
        except Vendor.DoesNotExist:
            return Response({'message': 'Vendor not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = VendorPerformanceSerializer(vendor)
        return Response(serializer.data, status=status.HTTP_200_OK)



