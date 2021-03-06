# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-03-26 06:39
from __future__ import unicode_literals

import common.utils
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetPermission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='名称')),
                ('is_active', models.BooleanField(default=True, verbose_name='激活')),
                ('date_expired', models.DateTimeField(default=common.utils.date_expired_default, verbose_name='过期日期')),
                ('created_by', models.CharField(blank=True, max_length=128, verbose_name='创建者')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='创建日期')),
                ('comment', models.TextField(blank=True, verbose_name='备注')),
                ('asset_groups', models.ManyToManyField(blank=True, related_name='granted_by_permissions', to='assets.AssetGroup', verbose_name='资产组')),
                ('assets', models.ManyToManyField(blank=True, related_name='granted_by_permissions', to='assets.Asset', verbose_name='资产')),
            ],
        ),
    ]
