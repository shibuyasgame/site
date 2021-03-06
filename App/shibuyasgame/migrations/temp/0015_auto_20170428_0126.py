# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-28 05:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shibuyasgame', '0014_auto_20170427_2322'),
    ]

    operations = [
        migrations.AddField(
            model_name='pin',
            name='booster',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pin',
            name='brand',
            field=models.CharField(default='Unbranded', max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pin',
            name='code',
            field=models.CharField(default=0, max_length=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='thread',
            name='code',
            field=models.CharField(default=0, max_length=3),
            preserve_default=False,
        ),
    ]
