# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-04 19:20
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('compare', '0004_auto_20180604_1858'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cmp_stop',
            name='stop_geom',
        ),
        migrations.AddField(
            model_name='cmp_stop',
            name='geom',
            field=django.contrib.gis.db.models.fields.PointField(geography=True, null=True, srid=4326),
        ),
    ]