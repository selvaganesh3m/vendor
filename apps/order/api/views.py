from rest_framework import generics
from rest_framework.views import APIView
from django.http import Http404
from apps.order.models import PurchaseOrder
from .serializers import PurchaseOrderSerializer
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction



class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

class PurchaseOrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

class VendorAcknowledgeMentAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    
    @transaction.atomic
    def put(self, request, po_number):
        user = request.user
        try:
            purchase_order = PurchaseOrder.objects.get(po_number=po_number, vendor__user=user)
        except PurchaseOrder.DoesNotExist:
            raise Http404
        if purchase_order.acknowledgement_date:
            return Response({"message":"Order already accepted."}, status=status.HTTP_202_ACCEPTED)
        purchase_order.acknowledgement_date = timezone.now()
        purchase_order.save()
        return Response({"message":"Vendor Accepted the Order."}, status=status.HTTP_200_OK)
    
class MarkOrderCompeted(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    
    @transaction.atomic
    def put(self, request, po_number):
        user = request.user
        try:
            purchase_order = PurchaseOrder.objects.get(po_number=po_number, vendor__user=user)
        except PurchaseOrder.DoesNotExist:
            raise Http404
        if not purchase_order.acknowledgement_date:
            return Response({"message":"You cannot COMPLETE the order befor accepting"}, status=status.HTTP_400_OK)
        if purchase_order.status == 'CANCELLED':
             return Response({"message":"Cannot proccess CANCELLED order."}, status=status.HTTP_204_NO_CONTENT)
        if purchase_order.status == 'COMPLETED':
            return Response({"message":"Order already marked as COMPLETED."}, status=status.HTTP_204_NO_CONTENT)
        purchase_order.status = 'COMPLETED'
        purchase_order.delivered_on = timezone.now().date()
        purchase_order.save()
        return Response({"message":"Order COMPLETED."}, status=status.HTTP_200_OK)


class MarkOrderCancelled(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    
    @transaction.atomic
    def put(self, request, po_number):
        user = request.user
        try:
            purchase_order = PurchaseOrder.objects.get(po_number=po_number, vendor__user=user)
        except PurchaseOrder.DoesNotExist:
            raise Http404
        if purchase_order.status == 'COMPLETED':
            return Response({"message":"You cannot CANCEL the completed order"}, status=status.HTTP_204_NO_CONTENT)
        if purchase_order.status == 'CANCELLED':
            return Response({"message":"Order Already CANCELLED"}, status=status.HTTP_204_NO_CONTENT)
        purchase_order.status = 'CANCELLED'
        purchase_order.save()
        return Response({"message":"Vendor Cancelled the Order."}, status=status.HTTP_200_OK)
