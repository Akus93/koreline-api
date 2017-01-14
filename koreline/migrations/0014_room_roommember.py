# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-01 20:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('koreline', '0013_auto_20161126_1243'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_open', models.BooleanField(default=True, verbose_name='Czy otwarty')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')),
                ('close_date', models.DateTimeField(auto_now_add=True, verbose_name='Data zamknięcia')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='koreline.Lesson', verbose_name='Lekcja')),
            ],
            options={
                'verbose_name_plural': 'Pokoje',
                'verbose_name': 'pokój',
            },
        ),
        migrations.CreateModel(
            name='RoomMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('join_date', models.DateTimeField(auto_now_add=True, verbose_name='Data dołączenia')),
                ('leave_date', models.DateTimeField(verbose_name='Data opuszczenia')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='koreline.UserProfile', verbose_name='Uczeń')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='koreline.Room', verbose_name='Pokój')),
            ],
            options={
                'verbose_name_plural': 'Zapisy do konwersacji',
                'verbose_name': 'zapis do konwersacji',
            },
        ),
    ]