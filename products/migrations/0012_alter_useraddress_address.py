# Generated by Django 5.0.6 on 2024-06-04 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_useraddress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraddress',
            name='address',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
