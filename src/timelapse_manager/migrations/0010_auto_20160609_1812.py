# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-09 18:12
from __future__ import unicode_literals

from django.db import migrations, models
import timelapse_manager.storage


class Migration(migrations.Migration):

    dependencies = [
        ('timelapse_manager', '0009_auto_20160609_1708'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='frame',
            options={'ordering': ('movie_rendering', 'number')},
        ),
        migrations.AddField(
            model_name='movierendering',
            name='file_md5',
            field=models.CharField(blank=True, db_index=True, default='', max_length=32),
        ),
        migrations.AlterField(
            model_name='movierendering',
            name='file',
            field=models.FileField(blank=True, db_index=True, default='', max_length=255, null=True, storage=timelapse_manager.storage.default_timelapse_storage, upload_to=timelapse_manager.storage.upload_to_movie_rendering),
        ),
    ]
