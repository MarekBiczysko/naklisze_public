# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-10 21:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_order_shipping_info'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, default='', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping_info',
            field=models.TextField(blank=True, default='', max_length=200, null=True),
        ),
    ]