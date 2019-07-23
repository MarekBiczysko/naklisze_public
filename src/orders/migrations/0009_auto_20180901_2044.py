# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-01 18:44
from __future__ import unicode_literals

from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_auto_20180826_0512'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='shipping_cost',
        ),
        migrations.AddField(
            model_name='order',
            name='products_cost_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('EUR', 'EUR €'), ('PLN', 'PLN zł'), ('USD', 'USD $')], default='PLN', editable=False, max_length=3),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_price',
            field=djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default=None, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('EUR', 'EUR €'), ('PLN', 'PLN zł'), ('USD', 'USD $')], default='PLN', editable=False, max_length=3),
        ),
        migrations.AddField(
            model_name='order',
            name='total_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('EUR', 'EUR €'), ('PLN', 'PLN zł'), ('USD', 'USD $')], default='PLN', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='order',
            name='products_cost',
            field=djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default=None, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='total',
            field=djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default=None, max_digits=10, null=True),
        ),
    ]
