#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from .models import *
from .write_sql import *
from zabbix.zbx_api import *
from celery import task

@task
def sync_host(list, node_id):
    for host in list:
        ''' 更新host '''
        time_now = int(time.time())
        res = Hosts.objects.filter(node_id=node_id, hostid=int(host['hostid'])).update(host=host['host'], status=int(host['status']), up_time=time_now, available=int(host['available']))
        if not res:
            Hosts.objects.create(node_id=node_id, hostid=int(host['hostid']), host=host['host'],
                                 status=int(host['status']), up_time=time_now, available=int(host['available']))

        ''' 更新interface '''
        interface_obj = host['interfaces'][0]
        host_obj = Hosts.objects.get(node_id=node_id, hostid=int(host['hostid']))
        res = Interface.objects.filter(node_id=node_id, interfaceid=int(interface_obj['interfaceid'])).update(
            type=int(interface_obj['type']), ip=interface_obj['ip'], port=interface_obj['port'], hostid=host_obj)
        if not res:
            Interface.objects.create(node_id=node_id, interfaceid=int(interface_obj['interfaceid']),
                                     type=int(interface_obj['type']), ip=interface_obj['ip'], port=interface_obj['port'], hostid=host_obj)
    return True

@task
def sync_template(list, node_id):
    for template in list:
        res = Hosts.objects.filter(node_id=node_id, hostid=int(template['templateid'])).update(host=template['host'],
                                                description=template['description'], status=int(template['status']))
        if not res:
            Hosts.objects.create(node_id=node_id, hostid=int(template['templateid']),
                                 host=template['host'], description=template['description'],
                                 status=int(template['status']))

@task
def sync_trigger(list, node_id):
    for trigger in list:
        time_now = int(time.time())
        trigger_data = write_trigger_tbl(trigger, node_id)

        if trigger_data['priority'] and trigger_data['priority'] < 3:
            trigger_data['priority'] = 1
        elif trigger_data['priority'] and trigger_data['priority'] > 3:
            trigger_data['priority'] = 5
        Triggers.objects.update_or_create(node_id=node_id, triggerid=int(trigger.get('triggerid')), defaults=trigger_data)

        for funtion in trigger.get('functions'):
            fun_data = write_functions_tbl(funtion, node_id)
            itemid = Items.objects.get(node_id=node_id, itemid=int(funtion['itemid']))
            triggerid = Triggers.objects.get(node_id=node_id, triggerid=int(funtion['triggerid']))
            Functions.objects.update_or_create(node_id=node_id, functionid=int(funtion['functionid']), defaults=fun_data)
            Functions.objects.filter(node_id=node_id, functionid=int(funtion['functionid'])).update(
                itemid=itemid, triggerid=triggerid)

    for trigger in list:
        if trigger['templateid'] != '0':
            father_trigger = Triggers.objects.get(node_id=node_id, triggerid=int(trigger['templateid']))
            Triggers.objects.filter(node_id=node_id, triggerid=int(trigger.get('triggerid'))).update(
                templateid=father_trigger, up_time=time_now)
        else:
            Triggers.objects.filter(node_id=node_id, triggerid=int(trigger.get('triggerid'))).update(
                templateid=None, up_time=time_now)
    return True

@task
def sync_item(list, node_id):
    for item in list:
        time_now = int(time.time())
        host_obj = Hosts.objects.get(node_id=node_id, hostid=int(item.get('hostid')))
        res = Items.objects.filter(node_id=node_id, itemid=int(item.get('itemid'))).update(hostid=host_obj,name=item['name'], type=int(item['type']), key_field=item['key_'], value_type=item['value_type'],
                                units=item['units'], status=item['status'], description=item['description'], delay=item['delay'], up_time=time_now)
        if not res:
            Items.objects.create(node_id=node_id, itemid=int(item.get('itemid')), hostid=host_obj, name=item['name'],
                                 type=int(item['type']),
                                 key_field=item['key_'], value_type=int(item['value_type']), units=item['units'],
                                 status=int(item['status']), description=item['description'], delay=item['delay'],
                                 up_time=time_now)

    for item in list:
        if item['templateid'] != '0':
            father_item = Items.objects.get(node_id=node_id, itemid=int(item['templateid']))
            Items.objects.filter(node_id=node_id, itemid=int(item.get('itemid'))).update(
                templateid=father_item)
        else:
            Items.objects.filter(node_id=node_id, itemid=int(item.get('itemid'))).update(
                templateid=None)

@task
def sync_item_trigger(item_list, trigger_list, node_id):
    ''' 注意: 先同步监控项，再同步触发器 '''
    sync_item(item_list, node_id)
    sync_trigger(trigger_list, node_id)

@task
def sync_all(host_list, template_list, node_id):
    sync_host(host_list, node_id)
    sync_template(template_list, node_id)

@task
def sync_all_host():
    node_list = Zabbix.objects.all()
    for node in node_list:
        host_list = get_zabbix_host_list(node)
        sync_host(host_list, node.id)
