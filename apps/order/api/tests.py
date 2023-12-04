from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import timedelta
from django.urls import reverse
from rest_framework import status

from apps.order.models import PurchaseOrder
from apps.vendor.models import Vendor


User = get_user_model()

class PurchaseOrderTest(TestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create_user(
            email='ankur@gmail.com', password='shukla')
        self.user2 = User.objects.create_user(
            email='likith@gmail.com', password='shukla')
        self.user3 = User.objects.create_user(
            email='deva@gmail.com', password='shukla')

        self.vendor1 = Vendor.objects.create(
            user=self.user1, name="ankur", contact_detail="india", address="india")
        self.vendor2 = Vendor.objects.create(
            user=self.user2, name="likith", contact_detail="india", address="india")
        
        
        self.delivery_date = timezone.now() + timedelta(days=7)
        self.past_date = timezone.now() + timedelta(days=-2)
        self.items1 = "[{\"note:3\"}]"
        self.items2 = "[{\"monitor:3\", \"cpu\"}: 3]"
        self.purchase_order1 = PurchaseOrder.objects.create(delivery_date=self.delivery_date, items=self.items1, quantity=1)
        self.purchase_order1 = PurchaseOrder.objects.create(delivery_date=self.delivery_date, items=self.items2, quantity=2)


    # GET purchase orders
    def test_get_purchase_orders(self):
        url = reverse('purchase-order-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), PurchaseOrder.objects.count())

    def test_get_purchase_orders_with_invalid_po_number(self):
        url = reverse('purchase-order-retrieve-update-destroy', args=["PO3e4s6a9s8-d"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Order not found.')

    

    def test_get_purchase_orders_by_valid_po_number(self):
        url = reverse('purchase-order-retrieve-update-destroy', args=[self.purchase_order1.po_number])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['items'], self.purchase_order1.items)
        self.assertEqual(response.data['quantity'], self.purchase_order1.quantity)

    # POST create purchase order
    def test_create_purchase_order_with_invalid_date(self):
        url = reverse('purchase-order-list-create')
        purchase_order_data = {
            "delivery_date": "12-12-12",
            "items": self.items2,
            "quantity": 2
        }
        
        response = self.client.post(url, data=purchase_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_purchase_order_with_past_date(self):
        url = reverse('purchase-order-list-create')
        purchase_order_data = {
            "delivery_date": self.past_date,
            "items": "[\"note:1\"]",
            "quantity": 1
        }
        
        response = self.client.post(url, data=purchase_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['delivery_date'][0], "Delivery date cannot be in the past.")

    def test_create_purchase_order_with_invalid_item_json(self):
        url = reverse('purchase-order-list-create')
        purchase_order_data = {
            "delivery_date": self.delivery_date,
            "items": ["note:1"],
            "quantity": 1
        }
        
        response = self.client.post(url, data=purchase_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['items'][0], 'Value must be valid JSON.')
    

    def test_create_purchase_order_with_quantity_zero(self):
        url = reverse('purchase-order-list-create')
        purchase_order_data = {
            "delivery_date": self.delivery_date,
            "items": "[\"note:1\"]",
            "quantity": 0
        }
        
        response = self.client.post(url, data=purchase_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['quantity'][0], 'Quantity must be a positive integer.')
    

    def test_create_purchase_order_with_negative_quantity(self):
        url = reverse('purchase-order-list-create')
        purchase_order_data = {
            "delivery_date": self.delivery_date,
            "items": "[\"note:1\"]",
            "quantity": -2
        }
        
        response = self.client.post(url, data=purchase_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['quantity'][0], 'Quantity must be a positive integer.')

    def test_create_order_success(self):
        url = reverse('purchase-order-list-create')
        purchase_order_data = {
            "delivery_date": self.delivery_date,
            "items": "[\"note:1\"]",
            "quantity": 1
        }
        
        response = self.client.post(url, data=purchase_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['items'], purchase_order_data['items'])
        self.assertEqual(response.data['quantity'], purchase_order_data['quantity'])


    # PUT Update purchase order
    def test_update_purchase_order_with_invalid_po_number(self):
        url = reverse('purchase-order-retrieve-update-destroy', args=["PO3e4s6a9s8-d"])
        purchase_order_data = {
            "delivery_date": self.delivery_date,
            "items": "[\"note:1\"]",
            "quantity": 1
        }
        response = self.client.put(
            url, data=purchase_order_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Order not found.')

    def test_update_po_with_invalid_delivery_date(self):
        url = reverse('purchase-order-retrieve-update-destroy', args=[self.purchase_order1.po_number])
        purchase_order_data = {
            "delivery_date": "203-12-12",
            "items": "[\"note:1\"]",
            "quantity": 1
        }
        response = self.client.put(
            url, data=purchase_order_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_po_with_past_delivery_date(self):
        url = reverse('purchase-order-retrieve-update-destroy', args=[self.purchase_order1.po_number])
        purchase_order_data = {
            "delivery_date": self.past_date,
            "items": "[\"note:1\"]",
            "quantity": 1
        }
        response = self.client.put(
            url, data=purchase_order_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['delivery_date'][0], 'Delivery date cannot be in the past.')

    def test_update_po_with_invalid_item_json(self):
        url = reverse('purchase-order-retrieve-update-destroy', args=[self.purchase_order1.po_number])
        purchase_order_data = {
            "delivery_date": self.delivery_date,
            "items": "[{\"note\"::1}]",
            "quantity": 1
        }
        response = self.client.put(
            url, data=purchase_order_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['items'][0], 'Invalid JSON format for items.')

    def test_update_po_with_quantity_zero(self):
        url = reverse('purchase-order-retrieve-update-destroy', args=[self.purchase_order1.po_number])
        purchase_order_data = {
            "delivery_date": self.delivery_date,
            "items": "[\"note:1\"]",
            "quantity": 0
        }
        response = self.client.put(
            url, data=purchase_order_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['quantity'][0], 'Quantity must be a positive integer.')
    def test_update_po_with_quantity_negative(self):
        url = reverse('purchase-order-retrieve-update-destroy', args=[self.purchase_order1.po_number])
        purchase_order_data = {
            "delivery_date": self.delivery_date,
            "items": "[\"note:1\"]",
            "quantity": -2
        }
        response = self.client.put(
            url, data=purchase_order_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['quantity'][0], 'Quantity must be a positive integer.')

    def test_update_po_success(self):
        url = reverse('purchase-order-retrieve-update-destroy', args=[self.purchase_order1.po_number])
        purchase_order_data = {
            "delivery_date": self.delivery_date,
            "items": [{"note":1, "laptop": 4}],
            "quantity": 2
        }
        response = self.client.put(
            url, data=purchase_order_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # DELETE delete purchase order
    def test_delete_po_with_invalid_po_number(self):
        url = reverse('purchase-order-retrieve-update-destroy', args=["PO3e4s6a9s8-d"])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Order not found.')


    def test_delete_po_success(self):
        url = reverse('purchase-order-retrieve-update-destroy', args=[self.purchase_order1.po_number])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(PurchaseOrder.DoesNotExist):
            PurchaseOrder.objects.get(po_number=self.purchase_order1.po_number)

