# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-13 20:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('koreline', '0026_auto_20170113_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia'),
        ),
    ]