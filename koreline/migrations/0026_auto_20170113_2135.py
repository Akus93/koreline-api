# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-13 20:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('koreline', '0025_accountoperation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(verbose_name='Kwota')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Czy oplacono')),
                ('create_date', models.DateTimeField(verbose_name='Data utworzenia')),
                ('pay_date', models.DateTimeField(blank=True, null=True, verbose_name='Data opłacenia')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='koreline.Lesson', verbose_name='Lekcja')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='koreline.UserProfile', verbose_name='Odbiorca')),
            ],
        ),
        migrations.AlterModelOptions(
            name='accountoperation',
            options={'verbose_name': 'operacja na koncie', 'verbose_name_plural': 'Operacje na koncie'},
        ),
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('INVITE', 'INVITE'), ('TEACHER_UNSUBSCRIBE', 'TEACHER_UNSUBSCRIBE'), ('STUDENT_UNSUBSCRIBE', 'STUDENT_UNSUBSCRIBE'), ('SUBSCRIBE', 'SUBSCRIBE'), ('COMMENT', 'COMMENT'), ('NEW_BILL', 'NEW_BILL')], max_length=32, verbose_name='Typ'),
        ),
    ]
