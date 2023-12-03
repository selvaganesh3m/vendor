from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.order.models import PurchaseOrder, Vendor

from .serializers import (AddRatingForOrderSerilaizer,
                          CreatePurchaseOrderSerializer,
                          PurchaseOrderSerializer,
                          UpdatePurchaseOrderSerializer)


class PurchaseOrderListCreateAPIView(APIView):

    def get(self, request, *args, **kwargs):
        purchase_orders = PurchaseOrder.objects.all()
        serializer = PurchaseOrderSerializer(purchase_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = CreatePurchaseOrderSerializer(data=request.data)

        if serializer.is_valid():
            order = serializer.save()
            serializer = PurchaseOrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateDestroyAPIView(APIView):

    def get_order(self, po_number):
        try:
            order = PurchaseOrder.objects.get(po_number=po_number)
        except PurchaseOrder.DoesNotExist:
            return None
        return order

    def get(self, request, po_number, *args, **kwargs):
        order = self.get_order(po_number)
        if not order:
            return Response({"message: Order not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PurchaseOrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, po_number, *args, **kwargs):
        order = self.get_order(po_number)
        if not order:
            return Response({"message: Order not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UpdatePurchaseOrderSerializer(
            order, data=request.data, partial=True)
        if serializer.is_valid():
            order = serializer.save()
            return Response({"message": "Order Updated successfully.", "order": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, po_number, *args, **kwargs):
        order = self.get_order(po_number)
        if not order:
            return Response({"message: Order not found."}, status=status.HTTP_404_NOT_FOUND)
        order.delete()
        return Response({'message': 'Order deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class AssignOrderToVendor(APIView):
    @transaction.atomic
    def put(self, request, po_number, vendor_code):
        try:
            purchase_order = PurchaseOrder.objects.get(
                po_number=po_number)
        except PurchaseOrder.DoesNotExist:
            return Response({'message': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            vendor = Vendor.objects.get(vendor_code=vendor_code)
        except Vendor.DoesNotExist:
            return Response({'message': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        if purchase_order.vendor:
            return Response({"message": "Order already assiged to another vendor."}, status=status.HTTP_409_CONFLICT)
        purchase_order.vendor = vendor
        purchase_order.issue_date = timezone.now()
        purchase_order.save()
        serializer = PurchaseOrderSerializer(purchase_order)
        return Response({"message": "Order assigned to vendor.", "order": serializer.data}, status=status.HTTP_200_OK)


class VendorAcknowledgeMentAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request, po_number):
        user = request.user
        try:
            purchase_order = PurchaseOrder.objects.get(
                po_number=po_number, vendor__user=user)
        except PurchaseOrder.DoesNotExist:
            return Response({'message': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        if purchase_order.acknowledgement_date:
            return Response({"message": "Order already accepted."}, status=status.HTTP_202_ACCEPTED)
        purchase_order.acknowledgement_date = timezone.now()
        purchase_order.save()
        return Response({"message": "Vendor Accepted the Order."}, status=status.HTTP_200_OK)


class MarkOrderCompeted(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request, po_number):
        user = request.user
        try:
            purchase_order = PurchaseOrder.objects.get(
                po_number=po_number, vendor__user=user)
        except PurchaseOrder.DoesNotExist:
            return Response({'message': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not purchase_order.acknowledgement_date:
            return Response({"message": "You cannot COMPLETE the order befor accepting"}, status=status.HTTP_400_BAD_REQUEST)
        if purchase_order.status == 'CANCELLED':
            return Response({"message": "Cannot proccess CANCELLED order."}, status=status.HTTP_204_NO_CONTENT)
        if purchase_order.status == 'COMPLETED':
            return Response({"message": "Order already marked as COMPLETED."}, status=status.HTTP_204_NO_CONTENT)
        purchase_order.status = 'COMPLETED'
        purchase_order.delivered_on = timezone.now().date()
        purchase_order.save()
        return Response({"message": "Order COMPLETED."}, status=status.HTTP_200_OK)


class MarkOrderCancelled(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request, po_number):
        user = request.user
        try:
            purchase_order = PurchaseOrder.objects.get(
                po_number=po_number, vendor__user=user)
        except PurchaseOrder.DoesNotExist:
            return Response({'message': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        if purchase_order.status == 'COMPLETED':
            return Response({"message": "You cannot CANCEL the completed order"}, status=status.HTTP_204_NO_CONTENT)
        if purchase_order.status == 'CANCELLED':
            return Response({"message": "Order Already CANCELLED"}, status=status.HTTP_204_NO_CONTENT)
        purchase_order.status = 'CANCELLED'
        purchase_order.save()
        return Response({"message": "Vendor Cancelled the Order."}, status=status.HTTP_200_OK)


class RateOrderAPIView(APIView):

    @transaction.atomic
    def put(self, request, po_number):
        try:
            purchase_order = PurchaseOrder.objects.get(po_number=po_number)
        except PurchaseOrder.DoesNotExist:
            return Response({'message': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not purchase_order.vendor or purchase_order.status == 'CANCELLED' or purchase_order.status == 'PENDING':
            return Response({"message": "You can rate only for the COMPLETED order."}, status=status.HTTP_403_FORBIDDEN)
        serializer = AddRatingForOrderSerilaizer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(purchase_order)
            serializer = PurchaseOrderSerializer(order)
            return Response({"message": "Order rated Successfully.", "order": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
