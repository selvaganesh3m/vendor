from django.urls import path
from .views import PurchaseOrderListCreateView, PurchaseOrderRetrieveUpdateDestroyView, VendorAcknowledgeMentAPIView, MarkOrderCancelled, MarkOrderCompeted

urlpatterns = [
    path('purchase-orders/', PurchaseOrderListCreateView.as_view(), name='purchase-order-list-create'),
    path('purchase-orders/<str:pk>/', PurchaseOrderRetrieveUpdateDestroyView.as_view(), name='purchase-order-retrieve-update-destroy'),
    path('purchase-orders/<str:po_number>/acknowledge/', VendorAcknowledgeMentAPIView.as_view(), name='vendor-acknowledgement'),
    path('purchase-orders/<str:po_number>/cancel/', MarkOrderCancelled.as_view(), name='cancel-purchase-order'),
    path('purchase-orders/<str:po_number>/complete/', MarkOrderCompeted.as_view(), name='complete-purchase-order')

]