# Generated by Django 4.2.7 on 2023-11-30 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_alter_purchaseorder_po_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='delivered_on',
            field=models.DateField(blank=True, null=True),
        ),
    ]
