# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-26 11:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('koreline', '0010_lesson_stage'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Data utworzenia'),
            preserve_default=False,
        ),
    ]
