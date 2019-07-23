# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-27 19:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('analytics', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='objectviewed',
            name='guest_email',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.GuestEmail'),
        ),
    ]