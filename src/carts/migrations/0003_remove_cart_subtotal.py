# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-26 02:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0002_remove_cart_shipping_cost'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='subtotal',
        ),
    ]