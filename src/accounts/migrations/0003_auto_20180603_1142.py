# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-03 09:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userslist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userslist',
            name='users',
        ),
        migrations.DeleteModel(
            name='UsersList',
        ),
    ]
