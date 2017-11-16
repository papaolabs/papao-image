# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-15 13:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vision_controller', '0002_auto_20171115_1222'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisionResults',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color_rgb', models.CharField(max_length=255)),
                ('color_score', models.CharField(max_length=255)),
                ('color_fraction', models.CharField(max_length=255)),
                ('label', models.CharField(max_length=255)),
                ('label_score', models.FloatField()),
            ],
        ),
        migrations.DeleteModel(
            name='ColorResults',
        ),
    ]
