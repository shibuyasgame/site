# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-28 09:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shibuyasgame', '0017_auto_20170428_0444'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='brv',
            field=models.PositiveIntegerField(default=10),
        ),
    ]
