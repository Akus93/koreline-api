# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-20 19:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('koreline', '0005_lesson_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_teacher',
            field=models.BooleanField(default=False),
        ),
    ]
