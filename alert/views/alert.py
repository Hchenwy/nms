#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import re
import urllib.parse
import time
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from alert.tasks import *
from zabbix.zbx_api import update_zabbix_trigger
from zabbix.mysqldb import Mysqlapi

def alert_list(request):
    if request.method == 'GET':
        try:
            hostid = int(request.GET.get('hostid'))
            nodeid = int(request.GET.get('nodeid'))
            priority = int(request.GET.get('priority'))
        except:
            hostid = 0
            nodeid = 1
            priority = 0
    pri_list = [{"name": "所有", "value": 0}, {"name": "灾难", "value": 5}, {"name": "严重", "value": 3}, {"name": "一般", "value": 1}]
    node_list = Zabbix.objects.all()
    host_list = Hosts.objects.filter(node_id=nodeid).exclude(status=3).order_by('name')
    app = u'监控信息'
    action = u'告警信息'

    return render(request, 'alert/alert_list.html', locals())

def alert_list_json(request):
    alert_list = []
    alert_json = {}
    if request.method == 'POST':
        try:
            print(request.POST)
            page_size = int(request.POST.get('page_size'))
            page_id = int(request.POST.get('page_id'))
            keyword = urllib.parse.unquote(request.POST.get('keyword'))
            father_node = int(request.POST.get('father_node'))
            host_id = int(request.POST.get('host_id'))
            priority = int(request.POST.get('priority'))
            state = int(request.POST.get('state'))
        except:
            print('data transport error!')
            return JsonResponse(alert_json)

        value_list = []
        priority_list = []
        join = join_condition = ''
        value_list.append(state)
        if priority:
            priority_list.append(priority)
        if host_id:
            join = 'INNER JOIN functions ON (functions.triggerid = triggers.triggerid) INNER JOIN items ON (items.itemid = functions.itemid)'
            join_condition = 'items.hostid = {hostid}'.format(hostid=host_id)

        node = Zabbix.objects.get(id=father_node)
        mysqlapi = Mysqlapi(user=node.zbx_mysql_user, password=node.zbx_mysql_passwd, db=node.zbx_mysql_db, host=node.zbx_mysql_host, port=node.zbx_mysql_port)

        alert_tbl = mysqlapi.select('triggers', description__icontains=keyword, value=value_list, priority=priority_list, status=0, lastchange__not=0, join=join, join_condition=join_condition)
        alert_num = len(alert_tbl)
        page_num = alert_num / page_size
        if page_num > int(page_num):
            page_num = int(page_num) + 1
        start_id = (page_id - 1) * page_size
        end_id = page_id * page_size
        alert_tbl = mysqlapi.select('triggers', description__icontains=keyword, value=value_list, priority=priority_list, status=0, lastchange__not=0,
                                    join=join, join_condition=join_condition, order_by='-lastchange', limit='{start},{num}'.format(start=start_id, num=page_size))
        for trigger in alert_tbl:
            dict = {}
            host = mysqlapi.get('hosts', join='INNER JOIN items ON (items.hostid = hosts.hostid) INNER JOIN functions ON (functions.itemid = items.itemid)',
                                join_condition='functions.triggerid = {triggerid}'.format(triggerid=trigger.get('triggerid')))
            interface = mysqlapi.get('interface', join='INNER JOIN hosts ON (hosts.hostid = interface.hostid) INNER JOIN items ON (items.hostid = hosts.hostid) INNER JOIN functions ON (functions.itemid = items.itemid)',
                                     join_condition='functions.triggerid = {triggerid}'.format(triggerid=trigger.get('triggerid')))  #Interface.objects.filter(hostid__items__functions__triggerid=trigger)
            description = re.sub("\{HOST.NAME\}", host.get('host'), trigger.get('description'))
            description = re.sub("\{HOST.IP\}", interface.get('ip'), description)

            dict['trigger_id'] = trigger.get('triggerid')
            dict['priority'] = trigger.get('priority')
            dict['host'] = host.get('host')
            dict['ip'] = interface.get('ip')
            dict['description'] = description
            dict['father_node'] = node.name
            dict['lastchange'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(trigger.get('lastchange')))
            dict['comments'] = trigger.get('comments')
            dict['value'] = trigger.get('value')
            alert_list.append(dict)

        alert_json['alert_list'] = alert_list
        alert_json['alert_num'] = alert_num
        alert_json['page_num'] = page_num

    return JsonResponse(alert_json)

def alert_edit(request):
    alert_json = {}
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('node_id'))
            trigger_id = int(request.POST.get('trigger_id'))
        except:
            print('get alert info error!')
            return JsonResponse(alert_json)

        node = Zabbix.objects.get(id=node_id)
        mysqlapi = Mysqlapi(user=node.zbx_mysql_user, password=node.zbx_mysql_passwd, db=node.zbx_mysql_db, host=node.zbx_mysql_host, port=node.zbx_mysql_port)
        trigger_obj = mysqlapi.get('triggers', triggerid=trigger_id)
        alert_json['comments'] = trigger_obj.get('comments')


    return JsonResponse(alert_json)

def alert_save(request):
    msg = ''
    if request.method == 'GET':
        try:
            trigger_id = int(request.GET.get('triggerid'))
            node_id = int(request.GET.get('nodeid'))
            comments = request.GET.get('comments')
        except:
            msg = u'数据传输异常'
            return HttpResponse(msg)

        node = Zabbix.objects.get(id=node_id)
        result = update_zabbix_trigger(node, {"triggerid": trigger_id, "comments": comments})
        if result.get('triggerids'):
            msg = u'成功编辑告警信息'
        else:
            msg = result.get('data')

    return HttpResponse(msg)
