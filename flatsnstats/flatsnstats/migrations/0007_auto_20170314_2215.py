# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-15 05:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flatsnstats', '0006_auto_20170314_2205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='ttp_last_updated',
            field=models.DateTimeField(default='2000-01-01T00:00:00Z'),
        ),
    ]