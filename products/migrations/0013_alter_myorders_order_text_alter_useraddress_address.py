# Generated by Django 5.0.6 on 2024-06-05 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_alter_useraddress_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myorders',
            name='order_text',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='address',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
