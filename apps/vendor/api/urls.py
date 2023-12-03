from django.urls import path
from .views import ListCreateVendorAPIView, VendorRetrieveUpdateDestroyAPIView, VendorPerformansAPIView

urlpatterns = [
    path('vendors/', ListCreateVendorAPIView.as_view(), name='vendor-list-create'),
    path('vendors/<str:vendor_code>/', VendorRetrieveUpdateDestroyAPIView.as_view(), name='vendor-retrieve-update-destroy'),
    path('vendors/<str:vendor_code>/performance/', VendorPerformansAPIView.as_view(), name='vendor-performance'),
]