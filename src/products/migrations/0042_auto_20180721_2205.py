# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-21 20:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0041_auto_20180613_0047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='button',
            name='description',
            field=models.TextField(default='\nPrzycisk spustu wykonany z tworzywa sztucznego.\nPosiada uniwersalny gwint pasujący do większości aparatów wyposażonych w spust z gwintem do wężyka spustowego.\nWklęsły kształt przycisku zwiększa komfort wykonywania zdjęć.\n'),
        ),
        migrations.AlterField(
            model_name='button',
            name='model',
            field=models.CharField(blank=True, choices=[('black', 'czarny'), ('red', 'czerwony'), ('silver', 'srebrny'), ('gold', 'złoty'), ('set', 'zestaw 4 kolorów')], max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name='strap',
            name='description',
            field=models.TextField(default='\nPasek nadgarstkowy zapewnia pasuje do wszystkich aparatów posiadających oczko do jego zamocowania.\nZapewnia wygodę i komfort trzymania aparatu, przydatny w szczególności przy fotografii ulicznej.\nRetro design pasuje także to nowoczesnych typów aparatów.\n'),
        ),
        migrations.AlterField(
            model_name='strap',
            name='model',
            field=models.CharField(blank=True, choices=[('rope', 'sznurowany'), ('leather_thin_black', 'skórzany cienki czarny'), ('leather_thin_brown', 'skórzany cienki brązowy'), ('leather_medium_black', 'skórzany średni czarny'), ('leather_medium_brown', 'skórzany średni brązowy'), ('leather_thick_black', 'skórzany gruby czarny'), ('leather_thick_brown_dark', 'skórzany gruby ciemny brązowy'), ('leather_thick_brown_light', 'skórzany cienki jasny brązowy')], max_length=120, null=True),
        ),
    ]
