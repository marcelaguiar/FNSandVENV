# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-07 00:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flatsnstats', '0002_toptrainingpartners_strava_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strava_id', models.IntegerField(default=0)),
                ('authorized', models.BooleanField()),
            ],
        ),
        migrations.RemoveField(
            model_name='toptrainingpartners',
            name='authorized',
        ),
    ]
