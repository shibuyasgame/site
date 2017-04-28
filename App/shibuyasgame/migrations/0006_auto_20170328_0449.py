# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-28 08:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shibuyasgame', '0005_charstats_req_mod'),
    ]

    operations = [
        migrations.RenameField(
            model_name='charstats',
            old_name='prsonality',
            new_name='personality',
        ),
        migrations.RemoveField(
            model_name='charstats',
            name='req_mod',
        ),
        migrations.AddField(
            model_name='charprofile',
            name='suffix',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]