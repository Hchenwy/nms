# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-03-26 06:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('ip', models.GenericIPAddressField(db_index=True, default='0.0.0.0', verbose_name='IP')),
                ('hostname', models.CharField(max_length=128, unique=True, verbose_name='资产名称')),
                ('monitor_id', models.IntegerField(blank=True, null=True, verbose_name='监控id')),
                ('is_active', models.BooleanField(default=True, verbose_name='激活')),
                ('type', models.CharField(blank=True, choices=[('Server', '服务器'), ('Switch', '交换机')], default='Server', max_length=16, null=True, verbose_name='资产类型')),
                ('env', models.CharField(blank=True, choices=[('Prod', '生产环境'), ('Dev', '开发环境'), ('Test', '测试环境')], default='Prod', max_length=8, null=True, verbose_name='资产环境')),
                ('status', models.CharField(blank=True, choices=[('In use', '使用中'), ('Out of use', '空闲中')], default='In use', max_length=12, null=True, verbose_name='资产状态')),
                ('public_ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='公网 IP')),
                ('remote_card_ip', models.CharField(blank=True, max_length=16, null=True, verbose_name='远程管理卡 IP')),
                ('cabinet_no', models.CharField(blank=True, max_length=32, null=True, verbose_name='机柜编号')),
                ('cabinet_pos', models.IntegerField(blank=True, null=True, verbose_name='机柜层号')),
                ('number', models.CharField(blank=True, max_length=32, null=True, verbose_name='资产编号')),
                ('vendor', models.CharField(blank=True, max_length=64, null=True, verbose_name='制造商')),
                ('model', models.CharField(blank=True, max_length=54, null=True, verbose_name='型号')),
                ('sn', models.CharField(blank=True, max_length=128, null=True, verbose_name='序列号')),
                ('cpu_model', models.CharField(blank=True, max_length=64, null=True, verbose_name='CPU型号')),
                ('cpu_count', models.IntegerField(blank=True, null=True, verbose_name='CPU数量')),
                ('cpu_cores', models.IntegerField(blank=True, null=True, verbose_name='CPU核数')),
                ('memory', models.CharField(blank=True, max_length=64, null=True, verbose_name='内存')),
                ('disk_total', models.CharField(blank=True, max_length=1024, null=True, verbose_name='硬盘大小')),
                ('disk_info', models.CharField(blank=True, max_length=1024, null=True, verbose_name='硬盘信息')),
                ('platform', models.CharField(blank=True, max_length=128, null=True, verbose_name='系统平台')),
                ('os', models.CharField(blank=True, max_length=128, null=True, verbose_name='操作系统')),
                ('os_version', models.CharField(blank=True, max_length=16, null=True, verbose_name='系统版本')),
                ('os_arch', models.CharField(blank=True, max_length=16, null=True, verbose_name='系统架构')),
                ('created_by', models.CharField(blank=True, max_length=32, null=True, verbose_name='创建者')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建日期')),
                ('comment', models.TextField(blank=True, default='', max_length=128, verbose_name='备注')),
            ],
        ),
        migrations.CreateModel(
            name='AssetGroup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='名称')),
                ('created_by', models.CharField(blank=True, max_length=32, verbose_name='创建者')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建日期')),
                ('comment', models.TextField(blank=True, verbose_name='备注')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='IDC',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32, verbose_name='名称')),
                ('bandwidth', models.CharField(blank=True, max_length=32, verbose_name='带宽')),
                ('contact', models.CharField(blank=True, max_length=128, verbose_name='联系人')),
                ('phone', models.CharField(blank=True, max_length=32, verbose_name='电话')),
                ('address', models.CharField(blank=True, max_length=128, verbose_name='地址')),
                ('intranet', models.TextField(blank=True, verbose_name='内网')),
                ('extranet', models.TextField(blank=True, verbose_name='外网')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建日期')),
                ('operator', models.CharField(blank=True, max_length=32, verbose_name='运营商')),
                ('created_by', models.CharField(blank=True, max_length=32, verbose_name='创建者')),
                ('comment', models.TextField(blank=True, verbose_name='备注')),
            ],
            options={
                'verbose_name': '机房',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='asset',
            name='IDC',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assets', to='assets.IDC', verbose_name='机房'),
        ),
        migrations.AddField(
            model_name='asset',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='assets', to='assets.AssetGroup', verbose_name='资产组'),
        ),
    ]
