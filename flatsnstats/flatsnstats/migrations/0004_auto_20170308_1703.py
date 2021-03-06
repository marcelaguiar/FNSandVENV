# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-09 01:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flatsnstats', '0003_auto_20170306_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='first_name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='users',
            name='last_name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='users',
            name='authorized',
            field=models.BooleanField(default=False),
        ),
    ]
