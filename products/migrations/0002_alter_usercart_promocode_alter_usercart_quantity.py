# Generated by Django 5.0.6 on 2024-05-19 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercart',
            name='promocode',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='usercart',
            name='quantity',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]