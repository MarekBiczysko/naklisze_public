# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-05 00:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0027_auto_20180304_2130'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='spec_table',
            field=models.TextField(blank=True, max_length=300, null=True),
        ),
    ]
