# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-16 14:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aws_controller', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Image',
        ),
    ]
