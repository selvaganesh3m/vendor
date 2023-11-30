from django.db import models
from apps.core.models import TimestampModel
from django.contrib.auth import get_user_model

 

User = get_user_model() 



class Vendor(TimestampModel):
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendors')
   name = models.CharField(max_length=125)
   contact_detail = models.TextField()
   address = models.TextField()
   vendor_code = models.CharField(max_length=20, unique=True)
   on_time_delivery_rate = models.FloatField()
   quality_rating_avg = models.FloatField()
   avg_response_time = models.FloatField()
   fulfillment_rate = models.FloatField()
   
   class Meta:
      db_table = 'vm_vendors'

   def __str__(self) -> str:
      return f'{self.name}'

   


