# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-28 11:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shibuyasgame', '0007_auto_20170328_0604'),
    ]

    operations = [
        migrations.AddField(
            model_name='charprofile',
            name='week',
            field=models.SmallIntegerField(default=15),
            preserve_default=False,
        ),
    ]
