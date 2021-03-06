# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-03 13:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

def forwards_func(apps, schema_editor):
    MyModel = apps.get_model('products', 'Product')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    new_ct = ContentType.objects.get_for_model(MyModel)
    MyModel.objects.filter(polymorphic_ctype__isnull=True).update(polymorphic_ctype=new_ct)

class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('products', '0012_auto_20180228_1938'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_products.product_set+', to='contenttypes.ContentType'),
        ),
        migrations.RunPython(forwards_func, migrations.RunPython.noop),
    ]

