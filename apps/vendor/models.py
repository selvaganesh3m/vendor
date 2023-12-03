from django.db import models
from apps.core.models import TimestampModel
from django.contrib.auth import get_user_model
from uuid import uuid4
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.db import transaction

 

User = get_user_model() 



class Vendor(TimestampModel):
   vendor_code = models.CharField(max_length=20, unique=True, primary_key=True, editable=False)
   user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor')
   name = models.CharField(max_length=125)
   contact_detail = models.TextField()
   address = models.TextField()
   on_time_delivery_rate = models.FloatField()
   quality_rating_avg = models.FloatField()
   avg_response_time = models.FloatField()
   fulfillment_rate = models.FloatField()
   
   class Meta:
      db_table = 'vm_vendors'

   def __str__(self) -> str:
      return f'{self.name}'
   
@receiver(pre_save, sender=Vendor)
@transaction.atomic
def vendor_pre_save_handler(sender, instance, *args, **kwargs):
    if not instance.vendor_code:
        instance.vendor_code = f'VC{str(uuid4())[:10]}'
        instance.on_time_delivery_rate = 0
        instance.quality_rating_avg = 0
        instance.avg_response_time = 0
        instance.fulfillment_rate = 0


   


