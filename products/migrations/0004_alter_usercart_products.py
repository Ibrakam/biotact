# Generated by Django 5.0.6 on 2024-05-19 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_remove_usercart_products_usercart_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercart',
            name='products',
            field=models.ManyToManyField(to='products.product'),
        ),
    ]