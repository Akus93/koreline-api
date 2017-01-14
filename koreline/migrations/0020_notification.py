# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-16 12:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('koreline', '0019_auto_20161211_2030'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, verbose_name='Tytuł')),
                ('text', models.CharField(max_length=255, verbose_name='Tekst')),
                ('is_read', models.BooleanField(default=False, verbose_name='Czy odczytane')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='koreline.UserProfile', verbose_name='Odbiorca')),
            ],
            options={
                'ordering': ['-create_date'],
                'verbose_name': 'Powiadomienie',
                'verbose_name_plural': 'Powiadomienia',
            },
        ),
    ]
