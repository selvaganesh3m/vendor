from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.vendor.models import Vendor
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


class GetVendorAPITest(TestCase):

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

    # GET Vendors

    def test_get_vendors(self):
        url = reverse('vendor-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), Vendor.objects.count())

    # GET Vendor Detail
    def test_get_vedor_with_invalid_vendor_code(self):
        url = reverse('vendor-retrieve-update-destroy',
                      args=["VCe3oqp4a3-d"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Vendor not found.')

    def test_get_vedor_detail_success(self):
        url = reverse('vendor-retrieve-update-destroy',
                      args=[self.vendor1.vendor_code])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.vendor1.name)
        self.assertEqual(
            response.data['vendor_code'], self.vendor1.vendor_code)
        self.assertEqual(
            response.data['vendor_code'], self.vendor1.vendor_code)
        self.assertEqual(
            response.data['contact_detail'], self.vendor1.contact_detail)
        self.assertEqual(
            response.data['on_time_delivery_rate'], self.vendor1.on_time_delivery_rate)
        self.assertEqual(
            response.data['quality_rating_avg'], self.vendor1.quality_rating_avg)
        self.assertEqual(
            response.data['avg_response_time'], self.vendor1.avg_response_time)
        self.assertEqual(
            response.data['fulfillment_rate'], self.vendor1.fulfillment_rate)

    # POST Create Vendor
    def test_create_vendor_with_unregistered_user_email(self):
        url = reverse('vendor-list-create')
        vendor_data = {
            "name": "Cameron",
            "contact_detail": "17, Roger Street, MG Road, Kolkatta",
            "address": "17, Roger Street, MG Road, Kolkatta",
            "user_email": "cameron@gmail.com"
        }
        response = self.client.post(url, data=vendor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()['user_email'][0], 'Register as user to become vendor.')

    def test_create_vendor_with_already_used_vendor_email(self):
        url = reverse('vendor-list-create')
        vendor_data = {
            "name": "Ankur Shukla",
            "contact_detail": "17, Roger Street, MG Road, Kolkatta",
            "address": "17, Roger Street, MG Road, Kolkatta",
            "user_email": "ankur@gmail.com"
        }
        response = self.client.post(url, data=vendor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()['user_email'][0], 'Email taken already.')

    def test_create_vendor_with_name_contains_other_than_alphabets(self):
        url = reverse('vendor-list-create')
        vendor_data = {
            "name": "Deva777",
            "contact_detail": "17, Roger Street, MG Road, Kolkatta",
            "address": "17, Roger Street, MG Road, Kolkatta",
            "user_email": "deva@gmail.com"
        }
        response = self.client.post(url, data=vendor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()['name'][0], 'Name should only contain letters and spaces.')

    def test_create_vendor_success(self):
        url = reverse('vendor-list-create')
        vendor_data = {
            "name": "Deva",
            "contact_detail": "17, Roger Street, MG Road, Kolkatta",
            "address": "17, Roger Street, MG Road, Kolkatta",
            "user_email": "deva@gmail.com"
        }
        response = self.client.post(url, data=vendor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'],
                         'Vendor created successfully')

    # PUT Update Vendor
    def test_update_vedor_with_invalid_vendor_code(self):
        url = reverse('vendor-retrieve-update-destroy',
                      args=["VCe3oqp4a3-d"])

        vendor_data = {
            "name": "Ankur Shukla333",
            "contact_detail": "17, Roger Street, MG Road, Kolkatta",
            "address": "17, Roger Street, MG Road, Kolkatta",
        }

        response = self.client.put(
            url, data=vendor_data, format='json', content_type='application/json')
        # response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Vendor not found.')

    def test_update_vendor_with_invalid_name(self):
        url = reverse('vendor-retrieve-update-destroy',
                      args=[self.vendor1.vendor_code])

        vendor_data = {
            "name": "Ankur Shukla333",
            "contact_detail": "17, Roger Street, MG Road, Kolkatta",
            "address": "17, Roger Street, MG Road, Kolkatta",
        }

        response = self.client.put(
            url, data=vendor_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()['name'][0], "Name should only contain letters and spaces.")

    def test_update_vendor_success(self):
        url = reverse('vendor-retrieve-update-destroy',
                      args=[self.vendor1.vendor_code])

        vendor_data = {
            "name": "Ankur Shukla Chvan",
            "contact_detail": "14, Ashok street, KGF, Karnataka",
            "address": "14, Ashok street, KGF, Karnataka",
        }

        response = self.client.put(
            url, data=vendor_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], vendor_data['name'])
        self.assertEqual(
            response.data['contact_detail'], vendor_data['contact_detail'])
        self.assertEqual(response.data['address'], vendor_data['address'])

    # DELETE delete vendor
    def test_delete_vedor_with_invalid_vendor_code(self):
        url = reverse('vendor-retrieve-update-destroy', args=["VCe3oqp4a3-d"])
        response=self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Vendor not found.')
        
        
    def test_delete_vedor_success(self):
        url = reverse('vendor-retrieve-update-destroy', args=[self.vendor1.vendor_code])
        response=self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Vendor.DoesNotExist):
            Vendor.objects.get(vendor_code=self.vendor1.vendor_code)

class VendorRelatedAPITest(TestCase):
    pass
        

