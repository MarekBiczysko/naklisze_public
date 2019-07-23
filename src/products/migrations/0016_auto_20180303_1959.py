# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-03 18:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0015_strap'),
    ]

    operations = [
        migrations.CreateModel(
            name='Button',
            fields=[
                ('product_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='products.Product')),
                ('color', models.CharField(blank=True, choices=[('black', 'Czarny'), ('red', 'Czerwony')], max_length=120, null=True)),
            ],
            options={
                'manager_inheritance_from_future': True,
            },
            bases=('products.product',),
        ),
        migrations.RemoveField(
            model_name='product',
            name='attribute1',
        ),
        migrations.RemoveField(
            model_name='product',
            name='attribute2',
        ),
        migrations.RemoveField(
            model_name='strap',
            name='type',
        ),
        migrations.AddField(
            model_name='strap',
            name='color',
            field=models.CharField(blank=True, choices=[('black_short', 'Krótki czarny'), ('brown_long', 'Długi brązowy')], max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]