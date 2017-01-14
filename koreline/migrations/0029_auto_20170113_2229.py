# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-13 21:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('koreline', '0028_auto_20170113_2216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('INVITE', 'INVITE'), ('TEACHER_UNSUBSCRIBE', 'TEACHER_UNSUBSCRIBE'), ('STUDENT_UNSUBSCRIBE', 'STUDENT_UNSUBSCRIBE'), ('SUBSCRIBE', 'SUBSCRIBE'), ('COMMENT', 'COMMENT'), ('NEW_BILL', 'NEW_BILL'), ('PAID_BILL', 'PAID_BILL'), ('DELETE_BILL', 'DELETE_BILL')], max_length=32, verbose_name='Typ'),
        ),
    ]
