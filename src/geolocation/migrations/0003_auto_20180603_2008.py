# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-03 18:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geolocation', '0002_geolocation_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geolocation',
            name='date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
