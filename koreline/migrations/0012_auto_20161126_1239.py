# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-26 11:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('koreline', '0011_lesson_create_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AlterModelOptions(
            name='lesson',
            options={'ordering': ['-create_date'], 'verbose_name': 'Lekcja', 'verbose_name_plural': 'Lekcje'},
        ),
        migrations.AddField(
            model_name='lessonmembership',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='koreline.Lesson', verbose_name='Lekcja'),
        ),
        migrations.AddField(
            model_name='lessonmembership',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='koreline.UserProfile', verbose_name='Uczeń'),
        ),
    ]
