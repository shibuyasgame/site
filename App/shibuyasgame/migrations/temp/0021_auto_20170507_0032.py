# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-07 04:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shibuyasgame', '0020_auto_20170507_0031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charprofile',
            name='mun',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='characters', to='shibuyasgame.UserProfile'),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='perp',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='log_entries', to='shibuyasgame.UserProfile'),
        ),
    ]
