from django.urls import path

from .views import (AssignOrderToVendor, MarkOrderCancelled, MarkOrderCompeted,
                    PurchaseOrderListCreateAPIView, RateOrderAPIView,
                    RetrieveUpdateDestroyAPIView, VendorAcknowledgeMentAPIView)

urlpatterns = [
    path('purchase-orders/', PurchaseOrderListCreateAPIView.as_view(), name='purchase-order-list-create'),
    path('purchase-orders/<str:po_number>/', RetrieveUpdateDestroyAPIView.as_view(), name='purchase-order-retrieve-update-destroy'),
    path('purchase-orders/<str:po_number>/acknowledge/', VendorAcknowledgeMentAPIView.as_view(), name='vendor-acknowledgement'),
    path('purchase-orders/<str:po_number>/cancel/', MarkOrderCancelled.as_view(), name='cancel-purchase-order'),
    path('purchase-orders/<str:po_number>/complete/', MarkOrderCompeted.as_view(), name='complete-purchase-order'),
    path('purchase-orders/<str:po_number>/assign/<str:vendor_code>/', AssignOrderToVendor.as_view(), name='assign-order-to-vendor'),
    path('purchase-orders/<str:po_number>/rate/', RateOrderAPIView.as_view(), name='rate-order'),
]
