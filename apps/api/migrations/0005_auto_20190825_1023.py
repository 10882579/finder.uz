# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-08-25 10:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_useraccount_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sessions',
            name='account',
        ),
        migrations.DeleteModel(
            name='Sessions',
        ),
    ]