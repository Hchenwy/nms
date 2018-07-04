#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import os
import re
import urllib.parse
import time
from ..forms import  NodeForm
from ..models.zabbix import Zabbix, Hosts, Items, Interface, Functions, Triggers, Groups, Hostsgroups, Itemskey, Hostmacro, Hoststemplates
from ..zbx_api import *
from ..write_sql import write_host_tbl, write_interface_tbl, write_template_tbl, write_trigger_tbl, write_functions_tbl, write_item_tbl
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django.core.urlresolvers import reverse
from django.core import serializers
from zabbix.tasks import *
from perms.utils import require_role
from zabbix.mysqldb import Mysqlapi



''' 节点管理 '''
def get_object(model, **kwargs):
    """
    use this function for query
    使用改封装函数查询数据库
    """
    for value in kwargs.values():
        if not value:
            return None

    the_object = model.objects.filter(**kwargs)
    if len(the_object) == 1:
        the_object = the_object[0]
    else:
        the_object = None
    return the_object

@require_role(role="admin")
def node_add(request):
    msg = ''
    data = {}
    if request.method == 'GET':
        try:
            nodeid = int(request.GET.get('nodeid'))
            data['name'] = request.GET.get('name')
            data['address'] = request.GET.get('address')
            data['bandwidth'] = request.GET.get('bandwidth')
            data['operator'] = request.GET.get('operator')
            data['contacts'] = request.GET.get('contacts')
            data['phone'] = request.GET.get('phone')
            data['zbx_user'] = request.GET.get('zbx_user')
            data['zbx_passwd'] = request.GET.get('zbx_passwd')
            data['zbx_ip'] = request.GET.get('zbx_ip')
            data['zbx_url'] = request.GET.get('zbx_url')
            data['zbx_mysql_user'] = request.GET.get('zbx_mysql_user')
            data['zbx_mysql_passwd'] = request.GET.get('zbx_mysql_passwd')
            data['zbx_mysql_db'] = request.GET.get('zbx_mysql_db')
            data['zbx_mysql_host'] = request.GET.get('zbx_mysql_host')
            data['zbx_mysql_port'] = request.GET.get('zbx_mysql_port')
            data['comment'] = request.GET.get('comment')
        except:
            return HttpResponse(u'数据传输异常')

        if not nodeid:  #新建节点
            if Zabbix.objects.filter(name=data.get('name')):
                return HttpResponse(u'已经存在名称为[%s]的节点'%data.get('name'))
            node = Zabbix(**data)
            node.save()

            ''' 创建节点的根群组 '''
            Groups.objects.create(name=node.name, internal=1, node_id=node.id, parentid=None)

            msg = u'新建节点[%s]成功。'%data.get('name')
        else:   #编辑节点
            if Zabbix.objects.filter(name=data.get('name')).exclude(id=nodeid):
                return HttpResponse(u'已经存在名称为[%s]的节点' % data.get('name'))
            Zabbix.objects.update_or_create(id=nodeid, defaults=data)
            msg = u'修改节点[%s]成功。' % data.get('name')
    return HttpResponse(msg)

@require_role(role="admin")
def node_edit(request):
    node_json = {}
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('node_id'))
        except:
            print('data transport error!')
            return JsonResponse(node_json)

        node_obj = Zabbix.objects.get(id=node_id)
        node_json["name"] = node_obj.name
        node_json['address'] = node_obj.address
        node_json['bandwidth'] = node_obj.bandwidth
        node_json['operator'] = node_obj.operator
        node_json['contacts'] = node_obj.contacts
        node_json['phone'] = node_obj.phone
        node_json['zbx_user'] = node_obj.zbx_user
        node_json['zbx_passwd'] = node_obj.zbx_passwd
        node_json['zbx_ip'] = node_obj.zbx_ip
        node_json['zbx_url'] = node_obj.zbx_url
        node_json['zbx_mysql_user'] = node_obj.zbx_mysql_user
        node_json['zbx_mysql_passwd'] = node_obj.zbx_mysql_passwd
        node_json['zbx_mysql_db'] = node_obj.zbx_mysql_db
        node_json['zbx_mysql_host'] = node_obj.zbx_mysql_host
        node_json['zbx_mysql_port'] = node_obj.zbx_mysql_port
        node_json['comment'] = node_obj.comment

    return JsonResponse(node_json)

@require_role(role="admin")
def node_del(request):
    msg = ''
    name_list = []
    name_nodelete_list = []
    if request.method == "GET":
        try:
            node_ids = request.GET.get('id')
            node_id_list = node_ids.split(',')
        except:
            return HttpResponse('数据传输异常！')

        for node_id in node_id_list:
            node_obj = Zabbix.objects.filter(id=node_id)
            if not Hosts.objects.filter(node_id=node_id):
                name_list.append(node_obj[0].name)
                node_obj.delete()
            else:
                name_nodelete_list.append(node_obj[0].name)
        msg = u'成功删除节点[%s]；'% ','.join(name_list)
        if name_nodelete_list:
            msg += u'节点[%s]下关联有主机，无法删除。'% ','.join(name_nodelete_list)

    return HttpResponse(msg)

@require_role(role="admin")
def node_list(request):
    node_num = len(Zabbix.objects.all())
    app = u'节点管理'
    action = u'节点列表'
    return render(request, 'zzabbix/node_list.html',locals())

@require_role(role="admin")
def node_list_json(request):
    node_json = {}
    node_list = []
    if request.method == 'POST':
        try:
            page_size = int(request.POST.get('page_size') or '10')
            page_id = int(request.POST.get('page_id') or '1')
            keyword = urllib.parse.unquote(request.POST.get('keyword')) or ''
        except:
            print('data transport error!')
            return JsonResponse(node_json)

        node_num = len(Zabbix.objects.filter(name__icontains=keyword))
        page_num = node_num/page_size
        if page_num > int(page_num):
            page_num = int(page_num) + 1
        start_id = (page_id - 1) * page_size
        end_id = page_id * page_size

        nodes = Zabbix.objects.filter(name__icontains=keyword).order_by('name')[start_id:end_id]
        for node in nodes:
            dict = {}
            dict['id'] = node.id
            dict['name'] = node.name
            dict['host_num'] = len(Hosts.objects.filter(node=node).exclude(status=3))
            dict['template_num'] = len(Hosts.objects.filter(node=node, status=3))
            dict['alert_num'] = len(Triggers.objects.filter(node=node, value=1, status=0))
            dict['zbx_status'] = node.zbx_status
            dict['date_added'] = node.date_added
            node_list.append(dict)

        node_json['node_list'] = node_list
        node_json['node_num'] = node_num
        node_json['page_num'] = page_num

    return JsonResponse(node_json)

@require_role(role="admin")
def sync_zabbix_all(request):
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('node_id'))
        except:
            return HttpResponse(u'数据传输异常，同步数据失败！')

        node = Zabbix.objects.get(id=node_id)
        host_list = get_zabbix_host_list(node)
        template_list = get_zabbix_template_list(node)
        sync_all.delay(host_list, template_list, node_id)

    return HttpResponse(u'后台正在同步数据，请稍等5-10分钟后再执行相关操作！')

''' 群组管理 '''
@require_role(role="user")
def group_list(request):
    node_list = Zabbix.objects.all()
    app = u'节点管理'
    action = u'群组管理'
    return render(request, 'zzabbix/group_list.html', locals())

@require_role(role="user")
def group_list_json(request):
    if request.method == 'POST':
        group_list = []
        group_json = {}
        try:
            node_id = int(request.POST.get('father_node'))
        except:
            return JsonResponse(group_json)
        groups = Groups.objects.filter(node_id=node_id)
        node = Zabbix.objects.get(id=node_id)
        for group in groups:
            host_num = len(Hosts.objects.filter(hostsgroups__groupid=group))
            dict = {}
            dict["id"] = group.id
            if group.parentid == None:
                dict["pId"] = group.parentid
            else:
                dict["pId"] = group.parentid.id
            dict["name"] = '%s(%s)' % (group.name, host_num)
            dict["internal"] = group.internal
            group_list.append(dict)

        group_json['group_list'] = group_list
    else:
        group_json = None

    return JsonResponse(group_json)

@require_role(role="user")
def group_get_host(request):
    host_json = {}
    host_sel_list = []
    host_list = []
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('father_node'))
            id = int(request.POST.get('id'))
        except:
            return JsonResponse(host_json)
        hosts_sel = Hosts.objects.filter(hostsgroups__groupid__id=id, node_id=node_id).exclude(status=3).order_by('host')
        hosts = Hosts.objects.filter(node_id=node_id).exclude(status=3).order_by('host')
        for host in hosts_sel:
            dict = {}
            dict['id'] = host.id
            dict['name'] = host.host
            host_sel_list.append(dict)
        for host in hosts:
            if host in hosts_sel:
                continue
            dict = {}
            dict['id'] = host.id
            dict['name'] = host.host
            host_list.append(dict)

        host_json['host_sel_list'] = host_sel_list
        host_json['host_list'] = host_list

    return JsonResponse(host_json)

@require_role(role="user")
def group_save(request):
    if request.method == 'POST':
        try:
            host_id = request.POST.get('host_id')
            group_id = int(request.POST.get('group_id'))
        except:
            return HttpResponse("发生未知错误，群组保存失败!")

        try:
            if host_id != '':
                host_id_list = host_id.split(',')
            else:
                host_id_list = []
            old_hosts = Hostsgroups.objects.filter(groupid=group_id)
            for host in old_hosts:
                if str(host.hostid.id) not in host_id_list:
                    Hostsgroups.objects.filter(hostid=host.hostid.id).delete()

            for id in host_id_list:
                hostid = Hosts.objects.get(id=int(id))
                groupid = Groups.objects.get(id=group_id)
                Hostsgroups.objects.get_or_create(hostid=hostid, groupid=groupid)

            return HttpResponse("群组保存成功!")
        except:
            return HttpResponse("群组保存失败!")

    return HttpResponse("")

@require_role(role="user")
def group_add(request):
    json_list = {}
    if request.method == 'POST':
        try:
            id = int(request.POST.get('parentid'))
            node_id = int(request.POST.get('father_node'))
        except:
            json_list['msg'] = u"添加新群组失败！"
            return JsonResponse(json_list)

        parentid = Groups.objects.get(id=id)
        Groups.objects.create(name='新群组', internal=0, node_id=node_id, parentid=parentid)
        json_list['msg'] = "ok"

    return JsonResponse(json_list)

@require_role(role="user")
def group_edit(request):
    json_list = {}
    if request.method == 'POST':
        try:
            id = int(request.POST.get('id') or '0')
            name = request.POST.get('name') or u'新群组'
            Groups.objects.filter(id=id).update(name=name)
            json_list['msg'] = 'ok'
        except:
            json_list['msg'] =('无法修改[%s]群组名称' % (name))

    return JsonResponse(json_list)

@require_role(role="user")
def group_del(request):
    json_list = {}
    if request.method == 'POST':
        try:
            id = int(request.POST.get('id') or '0')
            name = request.POST.get('name') or u'未知群组'
            host_num = len(Hosts.objects.filter(hostsgroups__groupid__id=id))
            if host_num != 0:
                json_list['msg'] = ('[%s]群组关联了%d台设备，无法删除！' % (name,host_num))
            else:
                Groups.objects.filter(id=id).delete()
                json_list['msg'] = ('成功删除[%s]群组。' % (name))

        except:
            json_list['msg'] = ('[%s]群组不存在！' % (name))

    return JsonResponse(json_list)

''' 设备管理 '''
@require_role(role="user")
def host_list(request):
    if request.method == 'GET':
        try:
            node_id = int(request.GET.get('nodeid'))
            group_id = int(request.GET.get('groupid'))
        except:
            node_id = 0
            group_id = 0

    node_list = Zabbix.objects.all()
    if len(node_list) > 0:
        if node_id == 0:
            groups_list = Groups.objects.filter(node_id=node_list[0].id)
        else:
            groups_list = Groups.objects.filter(node_id=node_id)

    for group in groups_list:
        group_obj = group
        group_name = group.name
        while group_obj.parentid:
            group_name = '%s_%s' % (group_obj.parentid.name, group_name)
            group_obj = group_obj.parentid
        group.name = group_name

    app = u'节点管理'
    action = u'设备管理'
    return render(request, 'zzabbix/host_list.html', locals())

@require_role(role="user")
def host_list_json(request):
    host_list = []
    host_json = {}
    if request.method == 'POST':
        try:
            page_size = int(request.POST.get('page_size'))
            page_id = int(request.POST.get('page_id'))
            keyword = urllib.parse.unquote(request.POST.get('keyword'))
            father_node = int(request.POST.get('father_node'))
            group_id = int(request.POST.get('group_id'))
        except:
            print('data transport error!')
            return JsonResponse(host_json)

        node = Zabbix.objects.get(id=father_node)
        mysqlapi = Mysqlapi(user=node.zbx_mysql_user, password=node.zbx_mysql_passwd, db=node.zbx_mysql_db, host=node.zbx_mysql_host, port=node.zbx_mysql_port)

        if group_id == 0:
            host_obj = Hosts.objects.filter(host__icontains=keyword, node_id=father_node).exclude(status=3)
        else:
            host_obj = Hosts.objects.filter(host__icontains=keyword, node_id=father_node, hostsgroups__groupid=group_id).exclude(status=3)

        host_num = len(host_obj)
        page_num = host_num / page_size
        if page_num > int(page_num):
            page_num = int(page_num) + 1
        start_id = (page_id - 1) * page_size
        end_id = page_id * page_size

        host_tbl = host_obj.order_by('host')[start_id:end_id]
        for host in host_tbl:
            dict = {}
            node = Zabbix.objects.get(id=father_node)
            interface = Interface.objects.get(hostid=host)
            if interface:
                dict['ip'] = interface.ip
                dict['type'] = interface.type
            dict['host_id'] = host.hostid
            dict['name'] = host.host
            dict['father_node'] = node.name
            dict['items_num'] = mysqlapi.select_count('items', hostid=host.hostid, flags=[0, 4])
            join = 'INNER JOIN functions ON (functions.triggerid = triggers.triggerid) INNER JOIN items ON (functions.itemid = items.itemid)'
            join_condition = 'items.hostid = {hostid}'.format(hostid=host.hostid)
            dict['trigger_num'] = mysqlapi.select_count('triggers', join=join, join_condition=join_condition, flags=[0, 4])
            dict['template'] = len(Hoststemplates.objects.filter(hostid=host))
            dict['available'] = host.available
            dict['status'] = host.status
            dict['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(host.up_time))
            host_list.append(dict)

        host_json['host_list'] = host_list
        host_json['host_num'] = host_num
        host_json['page_num'] = page_num

    return JsonResponse(host_json)

@require_role(role="user")
def host_sync_zabbix(request):
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('node_id'))

            node = Zabbix.objects.get(id=node_id)
            list = get_zabbix_host_list(node)
            sync_host.delay(list, node_id)
            '''for host in list:
                
                time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                print(time_now)
                res = Hosts.objects.filter(node_id=node_id, hostid=int(host['hostid'])).update(name=host['name'], status=int(host['status']), up_time=time_now, available=int(host['available']))
                if not res:
                    Hosts.objects.create(node_id=node_id, hostid=int(host['hostid']), name=host['name'], status=int(host['status']), up_time=time_now, available=int(host['available']))

                
                interface_obj = host['interfaces'][0]
                host_obj = Hosts.objects.get(node_id=node_id, hostid=int(host['hostid']))
                res = Interface.objects.filter(node_id=node_id, interfaceid=int(interface_obj['interfaceid'])).update(
                        type=int(interface_obj['type']), ip=interface_obj['ip'], port=interface_obj['port'], hostid=host_obj)
                if not res:
                    Interface.objects.create(node_id=node_id, interfaceid=int(interface_obj['interfaceid']),
                        type=int(interface_obj['type']), ip=interface_obj['ip'], port=interface_obj['port'], hostid=host_obj)'''


            return HttpResponse("同步设备数据已完成！")
        except:
            return HttpResponse("同步数据异常！")
    else:
        return HttpResponse(None)

@require_role(role="user")
def host_add(request):
    msg = ''
    if request.method == 'POST':
        try:
            host_id = int(request.POST.get('host_id'))
            node_id = int(request.POST.get('node_id'))
            status = int(request.POST.get('status'))
            type = int(request.POST.get('type'))
            name = request.POST.get('name')
            ip = request.POST.get('ip')
            port = request.POST.get('port')
            macro = request.POST.get('macro')
            value = request.POST.get('value')
            macro_list = macro.split(',')
            value_list = value.split(',')
            usemacro = []


            if len(macro_list) == len(value_list):
                for index in range(len(macro_list)):
                    if macro_list[index] != '':
                        dict= {}
                        dict['macro'] = macro_list[index]
                        dict['value'] = value_list[index]
                        usemacro.append(dict)
            node = Zabbix.objects.get(id=node_id)
            if host_id == 0:
                result = create_zabbix_host(node, type, name, status, ip, port, usemacro)
                if result.get('hostids'):
                    host_obj = Hosts.objects.create(node_id=node_id, hostid=int(result.get('hostids')[0]), host=name, status=status)

                    Interface.objects.create(hostid=host_obj, ip=ip, port=port, type=type)
                    if len(macro_list) == len(value_list):
                        for index in range(len(macro_list)):
                            if macro_list[index] != '':
                                Hostmacro.objects.create(hostid=host_obj, macro=macro_list[index], value=value_list[index])
                    msg = u'创建设备[%s]成功。' % name
                else:
                    msg = result.get('data')
            else:
                result = update_zabbix_host(node, host_id, type, name, status, ip, port, usemacro)
                if result.get('hostids'):
                    host_obj = Hosts.objects.filter(node_id=node_id, hostid=int(result.get('hostids')[0]))
                    host_obj.update(host=name, status=status)
                    Interface.objects.filter(hostid=host_obj[0]).update(ip=ip, port=port, type=type)
                    Hostmacro.objects.filter(hostid=host_obj[0]).delete()
                    if len(macro_list) == len(value_list):
                        for index in range(len(macro_list)):
                            if macro_list[index] != '':
                                Hostmacro.objects.create(hostid=host_obj, macro=macro_list[index], value=value_list[index])
                    msg = u'修改设备[%s]成功。' % name
                else:
                    msg = result.get('data')
        except:
            msg = u'数据传输异常！'

    return HttpResponse(msg)

@require_role(role="user")
def host_edit(request):
    host_json = {}
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('node_id'))
            host_id = int(request.POST.get('host_id'))
        except:
            print('data transport error!')
            return JsonResponse(host_json)

        host_obj = Hosts.objects.get(node_id=node_id, hostid=host_id)
        interface_obj = Interface.objects.get(hostid=host_obj)
        macro_obj = Hostmacro.objects.filter(hostid=host_obj)
        macro_list = []
        value_list = []
        for usemacro in macro_obj:
            macro_list.append(usemacro.macro)
            value_list.append(usemacro.value)
        host_json["name"] = host_obj.host
        host_json["status"] = host_obj.status
        host_json["type"] = interface_obj.type
        host_json["ip"] = interface_obj.ip
        host_json["port"] = interface_obj.port
        host_json["macro"] = ','.join(macro_list)
        host_json["value"] = ','.join(value_list)

    return JsonResponse(host_json)

@require_role(role="user")
def host_del(request):
    msg = ''
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('node_id'))
            host_id = request.POST.get('host_id')
            host_id_list = host_id.split(',')
            host_nodelete_list = []
            host_delete_list = []

            ''' 判断设备是否关联监控项 '''
            for id in host_id_list:
                host_obj = Hosts.objects.get(node_id=node_id, hostid=id)
                item_num = len(Items.objects.filter(hostid=host_obj))
                if item_num:
                    host_nodelete_list.append(host_obj.host)
                else:
                    host_delete_list.append(host_obj.host)

            if not host_nodelete_list:
                node = Zabbix.objects.get(id=node_id)
                result = delete_zabbix_host(node, host_id_list)
                if result.get('hostids'):
                    for id in result.get('hostids'):
                        host_obj = Hosts.objects.get(node_id=node_id, hostid=id)
                        Interface.objects.filter(hostid=host_obj).delete()
                        Hostmacro.objects.filter(hostid=host_obj).delete()
                        Hostsgroups.objects.filter(hostid=host_obj).delete()
                        Hoststemplates.objects.filter(hostid=host_obj).delete()
                        Hosts.objects.filter(node_id=node_id, hostid=id).delete()
                    msg = u'删除主机[%s]成功。' % ','.join(host_delete_list)
                else:
                    msg = result.get('data')
            else:
                msg = u'主机[%s]关联有监控项，请先删除关联的监控项！' % ','.join(host_nodelete_list)
        except:
            msg = u'数据传输异常，执行删除操作失败！'

    return HttpResponse(msg)


''' 模板管理 '''
@require_role(role="user")
def template_list(request):
    if request.method == 'GET':
        try:
            node_id = int(request.GET.get('nodeid'))
        except:
            node_id = 1

    node_list = Zabbix.objects.all()

    app = u'节点管理'
    action = u'模板管理'
    return render(request, 'zzabbix/template_list.html', locals())

@require_role(role="user")
def template_list_json(request):
    template_list = []
    template_json = {}
    if request.method == 'POST':
        print(request.POST)
        try:
            page_size = int(request.POST.get('page_size'))
            page_id = int(request.POST.get('page_id'))
            keyword = urllib.parse.unquote(request.POST.get('keyword'))
            father_node = int(request.POST.get('father_node'))
        except:
            print('data transport error')
            return JsonResponse(template_json)

        node = Zabbix.objects.get(id=father_node)
        mysqlapi = Mysqlapi(user=node.zbx_mysql_user, password=node.zbx_mysql_passwd, db=node.zbx_mysql_db, host=node.zbx_mysql_host, port=node.zbx_mysql_port)
        template_obj = Hosts.objects.filter(host__icontains=keyword, node_id=father_node, status=3)
        template_num = len(template_obj)
        page_num = template_num / page_size
        if page_num > int(page_num):
            page_num = int(page_num) + 1
        start_id = (page_id - 1) * page_size
        end_id = page_id * page_size
        host_tbl = template_obj.order_by('host')[start_id:end_id]
        for template in host_tbl:
            dict = {}
            node = Zabbix.objects.get(id=template.node_id)
            dict['host_id'] = template.hostid
            dict['name'] = template.host
            dict['father_node'] = node.name
            dict['items_num'] = mysqlapi.select_count('items', hostid=template.hostid, flags=[0, 4])
            join = 'INNER JOIN functions ON (functions.triggerid = triggers.triggerid) INNER JOIN items ON (functions.itemid = items.itemid)'
            join_condition = 'items.hostid = {hostid}'.format(hostid=template.hostid)
            dict['trigger_num'] = mysqlapi.select_count('triggers', join=join, join_condition=join_condition, flags=[0, 4])
            dict['host'] = len(Hoststemplates.objects.filter(templateid=template))
            template_list.append(dict)

        template_json['host_list'] = template_list
        template_json['host_num'] = template_num
        template_json['page_num'] = page_num

    return JsonResponse(template_json)

@require_role(role="user")
def template_sync_zabbix(request):
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('node_id'))

            node = Zabbix.objects.get(id=node_id)
            list = get_zabbix_template_list(node)
            sync_template.delay(list, node_id)
            '''for template in list:
                res = Hosts.objects.filter(node_id=node.id, hostid=int(template['templateid'])).update(host=template['host'],
                                                description=template['description'], status=int(template['status']))
                if not res:
                    Hosts.objects.create(node_id=node.id, hostid=int(template['templateid']),
                        host=template['host'], description=template['description'], status=int(template['status']))'''
            return HttpResponse("同步模板数据已完成！")
        except:
            return HttpResponse("同步数据异常！")
    else:
        return HttpResponse(None)

@require_role(role="user")
def template_get_host(request):
    host_json = {}
    host_sel_list = []
    host_list = []
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('node_id'))
            template_id = int(request.POST.get('template_id'))
        except:
            print("data transport error!")
            return JsonResponse(host_json)


        if template_id == 0:
            host_sel = []
            host_json['name'] = ''
            host_json['description'] = ''
        else:
            template_obj = Hosts.objects.get(hostid=template_id, node_id=node_id)
            host_json['name'] = template_obj.host
            host_json['description'] = template_obj.description
            hosttemp_list = template_obj.ht_template.all()
            host_sel = [hosttemp.hostid for hosttemp in hosttemp_list]

        hosts = Hosts.objects.filter(node_id=node_id).exclude(status=3)
        for host in host_sel:
            dict = {}
            dict['host_id'] = host.hostid
            dict['name'] = host.host
            host_sel_list.append(dict)
        for host in hosts:
            if host in host_sel:
                continue
            dict = {}
            dict['host_id'] = host.hostid
            dict['name'] = host.host
            host_list.append(dict)

        host_json['host_sel_list'] = host_sel_list
        host_json['host_list'] = host_list

    return JsonResponse(host_json)

@require_role(role="user")
def template_add(request): #新增和修改
    msg = ''
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('node_id'))
            template_id = int(request.POST.get('template_id'))
            name = request.POST.get('name')
            description = request.POST.get('description')
            host_id = request.POST.get('host_id')
            if host_id != '':
                host_id_list = host_id.split(',')
            else:
                host_id_list = []
        except:
            print('data transport error!')
            return HttpResponse(u'数据传输异常！')

        ''' 判断模板和主机的监控项和触发器同步条件 '''
        node = Zabbix.objects.get(id=node_id)
        hostid_list = [{"hostid": id} for id in host_id_list if id != '']
        if template_id == 0:    #template_id==0，新增模板
            result = create_zabbix_template(node, name, description, hostid_list)
            if result.get('templateids'):
                template_obj = Hosts.objects.create(node_id=node_id, hostid=int(result.get('templateids')[0]),
                                                    host=name, status=3, description=description)
                for host_id in host_id_list:
                    host_obj = Hosts.objects.get(node_id=node_id, hostid=int(host_id))
                    Hoststemplates.objects.create(hostid=host_obj, templateid=template_obj)
                msg = u'创建模板[%s]成功。' % name
            else:
                msg = result.get('data')
        else:
            result = update_zabbix_template(node, template_id, name, description, hostid_list)
            if result.get('templateids'):
                Hosts.objects.filter(node_id=node_id, hostid=int(result.get('templateids')[0])).update(host=name, status=3, description=description)
                template_obj = Hosts.objects.get(node_id=node_id, hostid=int(result.get('templateids')[0]))
                ht_list = Hoststemplates.objects.filter(templateid=template_obj)
                ht_pk_list = [ht.hostid.hostid for ht in ht_list]
                host_pk_list = []
                change_hostids = []
                for host_id in host_id_list: #遍历主机列表，数据库没有记录的则新建记录
                    host_obj = Hosts.objects.get(node_id=node_id, hostid=int(host_id))
                    host_pk_list.append(host_obj.hostid)
                    if int(host_id) not in ht_pk_list:
                        Hoststemplates.objects.create(templateid=template_obj, hostid=host_obj)
                        change_hostids.append(host_id)
                for host_id in ht_pk_list:   #遍历数据库hoststemplates表，不在主表中的记录删除。
                    if host_id not in host_pk_list:
                        host_obj = Hosts.objects.get(node_id=node_id, hostid=int(host_id))
                        Hoststemplates.objects.filter(templateid=template_obj, hostid=host_obj).delete()
                        change_hostids.append(str(host_id))

                ''' 同步zabbix监控项和触发器到本地数据库 
                if change_hostids:
                    item_list = get_zabbix_items_list(node, change_hostids)
                    trigger_list = get_zabbix_trigger_list(node, change_hostids)
                    sync_item_trigger.delay(item_list, trigger_list, node_id)'''

                msg = u'修改模板[%s]成功。' % name
            else:
                msg = result.get('data')

    return HttpResponse(msg)

@require_role(role="user")
def template_del(request):
    msg = ''
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('node_id'))
            template_id_list = request.POST.get('template_id').split(',')
            template_nodelete_list = []
            template_delete_list = []


            ''' 判断模板是否关联主机 '''
            for id in template_id_list:
                template_obj = Hosts.objects.get(node_id=node_id, hostid=id)
                host_num = len(Hoststemplates.objects.filter(templateid=template_obj))
                if host_num:
                    template_nodelete_list.append(template_obj.host)
                else:
                    template_delete_list.append(template_obj.host)

            if not template_nodelete_list:
                node = Zabbix.objects.get(id=node_id)
                result = delete_zabbix_template(node, template_id_list)
                if result.get('templateids'):
                    for id in result.get('templateids'):
                        template_obj = Hosts.objects.get(node_id=node_id, hostid=id)
                        Hoststemplates.objects.filter(templateid=template_obj).delete()
                        Hosts.objects.filter(node_id=node_id, hostid=id).delete()
                    msg = u'删除模板[%s]成功。' % ','.join(template_delete_list)
                else:
                    msg = result.get('data')
            else:
                msg = u'模板[%s]关联有主机，请先删除关联的主机！' % ','.join(template_nodelete_list)
        except:
            msg = u'数据传输异常，执行删除操作失败！'

    return HttpResponse(msg)


''' 监控项管理 '''
@require_role(role="user")
def item_list(request):
    if request.method == 'GET':
        try:
            hostid = int(request.GET.get('hostid'))
            nodeid = int(request.GET.get('nodeid'))
        except:
            hostid = 0
            nodeid = 1
        try:
            father_item_id = int(request.GET.get('itemid'))
        except:
            father_item_id = 0

    node_list = Zabbix.objects.all()
    host_list = Hosts.objects.filter(node_id=nodeid).order_by('host')
    app = u'节点管理'
    action = u'监控项管理'
    return render(request, 'zzabbix/item_list.html', locals())

@require_role(role="user")
def item_list_json(request):
    item_list = []
    item_json = {}
    if request.method == 'POST':
        try:
            page_size = int(request.POST.get('page_size'))
            page_id = int(request.POST.get('page_id'))
            keyword = urllib.parse.unquote(request.POST.get('keyword'))
            father_node = int(request.POST.get('father_node'))
            host_id = int(request.POST.get('host_id'))
        except:
            print('data transport error!')
            return JsonResponse(item_json)

        node = Zabbix.objects.get(id=father_node)
        mysqlapi = Mysqlapi(user=node.zbx_mysql_user, password=node.zbx_mysql_passwd, db=node.zbx_mysql_db, host=node.zbx_mysql_host, port=node.zbx_mysql_port)
        if host_id == 0:
            item_num = mysqlapi.select_count('items', name__icontains=keyword, flags=[0, 4])
        else:
            join = 'INNER JOIN hosts ON (items.hostid = hosts.hostid)'
            join_condition = 'hosts.hostid = {hostid}'.format(hostid=host_id)
            item_num = mysqlapi.select_count('items', name__icontains=keyword, join=join, join_condition=join_condition, flags=[0, 4])

        page_num = item_num / page_size
        if page_num > int(page_num):
            page_num = int(page_num) + 1
        start_id = (page_id - 1) * page_size
        end_id = page_id * page_size
        if host_id == 0:
            item_tbl = mysqlapi.select('items', name__icontains=keyword, flags=[0, 4], order_by='name', limit='{start},{end}'.format(start=start_id, end=end_id))
        else:
            item_tbl = mysqlapi.select('items', name__icontains=keyword, join=join, join_condition=join_condition, flags=[0, 4], order_by='name', limit='{start},{num}'.format(start=start_id,  num=page_size))
        for item in item_tbl:
            dict = {}
            join = 'INNER JOIN items ON (items.hostid = hosts.hostid)'
            join_condition = 'items.itemid = {itemid}'.format(itemid=item.get('itemid'))
            host = mysqlapi.get('hosts', join=join, join_condition=join_condition)
            if item.get('templateid'):
                item_dict = mysqlapi.get('items', itemid=item.get('templateid'))
                father_host = mysqlapi.get('hosts', join='INNER JOIN items ON (items.hostid = hosts.hostid)',
                                           join_condition='items.itemid = {itemid}'.format(itemid=item_dict.get('itemid')))
                dict['father_host'] = father_host.get('host')

            dict['item_id'] = item.get('itemid')
            dict['host'] = host.get('host')
            dict['name'] = item.get('name')
            dict['key_'] = item.get('key_')
            dict['trigger_num'] = mysqlapi.select_count('functions', itemid=item.get('itemid'))
            dict['delay'] = item.get('delay')
            dict['status'] = item.get('status')
            dict['description'] = item.get('description')
            dict['father_node'] = node.name
            item_list.append(dict)

        item_json['item_list'] = item_list
        item_json['item_num'] = item_num
        item_json['page_num'] = page_num

    return JsonResponse(item_json)

@require_role(role="user")
def item_sync_zabbix(request):
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('node_id'))
            print('item_sync_zabbix')

            node = Zabbix.objects.get(id=node_id)
            host_list = get_zabbix_host_list(node)
            template_list = get_zabbix_template_list(node)
            templateids = [template.get('templateid') for template in template_list]

            item_list = get_zabbix_items_list(node, templateids=templateids)
            #sync_item.delay(item_list, node_id) #celery 任务
            for i in range(0, len(host_list), 100):
                hostids = [host.get('hostid') for host in host_list[i:i+100]]
                item_list += get_zabbix_items_list(node, hostids=hostids)
                print('host_list[%s]'% i)
            print(len(item_list))
            sync_item.delay(item_list, node_id) # celery 任务

            return HttpResponse("同步监控项数据已完成！")
        except:
            return HttpResponse("同步数据异常！")
    else:
        return HttpResponse(None)

@require_role(role="user")
def item_get_key(request):
    key_json = {}
    key_list = []
    if request.method == 'POST':
        try:
            key_type = int(request.POST.get('key_type'))
        except:
            print('get item key fail!')
            return JsonResponse(key_json)

        item_key_list = Itemskey.objects.filter(type=key_type)
        if key_type == 7:
            item_key_list_2 = Itemskey.objects.filter(type=0)
            for item_key in item_key_list_2:
                dict = {}
                dict['key'] = item_key.key
                dict['description'] = item_key.description
                key_list.append(dict)

        for item_key in item_key_list:
            dict = {}
            dict['key'] = item_key.key
            dict['description'] = item_key.description
            key_list.append(dict)
        key_json['key_list'] = key_list

    return JsonResponse(key_json)

@require_role(role="user")
def item_add(request):
    param_dict = {}
    if request.method == 'GET':
        try:
            node_id = int(request.GET.get('nodeid'))
            item_id = int(request.GET.get('itemid'))
            host_id = int(request.GET.get('hostid'))
            param_dict['name'] = request.GET.get('name')
            param_dict['type'] = request.GET.get('type')
            param_dict['key_'] = request.GET.get('key')
            param_dict['value_type'] = request.GET.get('value-type')
            param_dict['units'] = request.GET.get('units')
            param_dict['delta'] = request.GET.get('delta')
            param_dict['delay'] = request.GET.get('delay')
            param_dict['status'] = request.GET.get('status')
            param_dict['description'] = request.GET.get('description')
            param_dict['snmp_oid'] = request.GET.get('snmp_oid')
            param_dict['snmp_community'] = request.GET.get('snmp_community')

            node = Zabbix.objects.get(id=node_id)
            if item_id == 0:    #新增监控项
                interface = Interface.objects.filter(hostid__hostid=host_id, hostid__node_id=node_id)
                if interface:
                    param_dict['interfaceid'] = interface[0].interfaceid
                param_dict['hostid'] = host_id
                result = create_zabbix_item(node, param_dict)
                if result.get('itemids'):
                    return HttpResponse(u'创建监控项[%s]成功。' % param_dict['name'])
                else:
                    return HttpResponse(result.get('data'))
            else:   #编辑监控项
                param_dict['itemid'] = item_id
                result = update_zabbix_item(node, param_dict)
                if result.get('itemids'):
                    return HttpResponse(u'修改监控项[%s]成功。' % param_dict['name'])
                else:
                    return HttpResponse(result.get('data'))
        except:
            return HttpResponse(u'数据传输异常！')
    return HttpResponse('')

@require_role(role="user")
def item_edit(request):
    item_json = {}
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('node_id'))
            item_id = int(request.POST.get('item_id'))
        except:
            print('data transport error!')
            return JsonResponse(item_json)

        node = Zabbix.objects.get(id=node_id)
        mysqlapi = Mysqlapi(user=node.zbx_mysql_user, password=node.zbx_mysql_passwd, db=node.zbx_mysql_db, host=node.zbx_mysql_host, port=node.zbx_mysql_port)
        item_obj = mysqlapi.get('items', itemid=item_id)
        if item_obj.get('templateid'):
            father_host = mysqlapi.get('hosts', join='INNER JOIN items ON (items.hostid = hosts.hostid)', join_condition='items.itemid = {itemid}'.format(itemid=item_obj.get('templateid')))
            item_json['father_item_id'] = item_obj.get('templateid')
            item_json['father_name'] = father_host.get('host')
            item_json['father_id'] = father_host.get('hostid')

        item_json["name"] = item_obj.get('name')
        item_json["type"] = item_obj.get('type')
        item_json["key"] = item_obj.get('key_')
        item_json["value_type"] = item_obj.get('value_type')
        item_json["units"] = item_obj.get('units')
        item_json["delta"] = 0
        item_json["delay"] = item_obj.get('delay')
        item_json["status"] = item_obj.get('status')
        item_json["description"] = item_obj.get('description')

    return JsonResponse(item_json)

@require_role(role="user")
def item_del(request):
    msg = ''
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('node_id'))
            item_id = request.POST.get('item_id')
            item_id_list = item_id.split(',')
        except:
            msg = u'数据传输异常，执行删除操作失败！'
            return HttpResponse(msg)

        node = Zabbix.objects.get(id=node_id)
        result = delete_zabbix_item(node, item_id_list)
        if result.get('itemids'):
            msg = u'删除监控项成功。'
        else:
            msg = result.get('data')

    return HttpResponse(msg)

''' 触发器管理 '''
@require_role(role="user")
def trigger_list(request):
    if request.method == 'GET':
        try:
            hostid = int(request.GET.get('hostid'))
            nodeid = int(request.GET.get('nodeid'))
        except:
            hostid = 0
            nodeid = 1
        try:
            father_tri_id = int(request.GET.get('triggerid'))
        except:
            father_tri_id = 0

    node_list = Zabbix.objects.all()
    host_list = Hosts.objects.filter(node_id=nodeid).order_by('host')
    app = u'配置管理'
    action = u'触发器管理'
    return render(request, 'zzabbix/trigger_list.html', locals())

@require_role(role="user")
def tri_add_item(request):
    item_json = {}
    item_list = []
    if request.method == 'POST':
        try:
            host_id = int(request.POST.get('host_id'))
            node_id = int(request.POST.get('node_id'))
            trigger_id = int(request.POST.get('trigger_id'))
        except:
            print('data transport error!')
            return JsonResponse(item_json)

        node = Zabbix.objects.get(id=node_id)
        mysqlapi = Mysqlapi(user=node.zbx_mysql_user, password=node.zbx_mysql_passwd, db=node.zbx_mysql_db, host=node.zbx_mysql_host, port=node.zbx_mysql_port)
        if host_id:
            host_obj = mysqlapi.get('hosts', hostid=host_id)
        elif trigger_id:
            host_obj = mysqlapi.get('hosts', join='INNER JOIN items ON (items.hostid = hosts.hostid) INNER JOIN functions ON (functions.itemid = items.itemid)',
                                    join_condition='functions.triggerid = {triggerid}'.format(triggerid=trigger_id))

        item_tbl = mysqlapi.select('items', hostid=host_id)
        for item in item_tbl:
            dict = {}
            dict['id'] = item.get('itemid')
            dict['name'] = item.get('name')
            dict['key_'] = item.get('key_')
            item_list.append(dict)

        item_json['item_list'] = item_list
        item_json['node_name'] = Zabbix.objects.get(id=node_id).name
        item_json['host_name'] = host_obj.get('host')

    return JsonResponse(item_json)

@require_role(role="user")
def trigger_list_json(request):
    trigger_list = []
    trigger_json = {}
    if request.method == 'POST':
        try:
            page_size = int(request.POST.get('page_size'))
            page_id = int(request.POST.get('page_id'))
            keyword = urllib.parse.unquote(request.POST.get('keyword'))
            father_node = int(request.POST.get('father_node'))
            host_id = int(request.POST.get('host_id'))
        except:
            print('data transport error!')
            return JsonResponse(trigger_json)

        node = Zabbix.objects.get(id=father_node)
        mysqlapi = Mysqlapi(user=node.zbx_mysql_user, password=node.zbx_mysql_passwd, db=node.zbx_mysql_db, host=node.zbx_mysql_host, port=node.zbx_mysql_port)
        ''' 获取当页数据，页数，总数据量 '''
        if host_id == 0:
            trigger_num = mysqlapi.select_count('triggers', description__icontains=keyword, flags=[0, 4])
        else:
            trigger_num = mysqlapi.select_count('triggers', description__icontains=keyword,
                    join='INNER JOIN functions ON (functions.triggerid = triggers.triggerid) INNER JOIN items ON (functions.itemid = items.itemid)',
                    join_condition='items.hostid = {hostid}'.format(hostid=host_id), flags=[0, 4])
        page_num = trigger_num / page_size
        if page_num > int(page_num):
            page_num = int(page_num) + 1
        start_id = (page_id - 1) * page_size
        if host_id == 0:
            trigger_tbl = mysqlapi.select('triggers', description__icontains=keyword, flags=[0, 4], order_by='-priority', limit='{start},{num}'.format(start=start_id, num=page_size))
        else:
            trigger_tbl = mysqlapi.select('triggers', description__icontains=keyword,
                    join='INNER JOIN functions ON (functions.triggerid = triggers.triggerid) INNER JOIN items ON (functions.itemid = items.itemid)',
                    join_condition='items.hostid = {hostid}'.format(hostid=host_id), flags=[0, 4], order_by='-priority', limit='{start},{num}'.format(start=start_id, num=page_size))
        for trigger in trigger_tbl:
            dict = {}
            function_obj = mysqlapi.select('functions', triggerid=trigger.get('triggerid'))
            host = mysqlapi.get('hosts', join='INNER JOIN items ON (items.hostid = hosts.hostid) INNER JOIN functions ON (functions.itemid = items.itemid)',
                    join_condition='functions.triggerid = {triggerid}'.format(triggerid=trigger.get('triggerid')))
            item = mysqlapi.get('items', join='INNER JOIN functions ON (functions.itemid = items.itemid)', join_condition='functions.triggerid = {triggerid}'.format(triggerid=trigger.get('triggerid')))
            for funtion in function_obj:
                exp_str = "%s:%s.%s(%s)" % (host.get('host'), item.get('key_'), funtion.get('function'), funtion.get('parameter'))
                trigger['expression'] = re.sub(str(funtion.get('functionid')), exp_str, trigger.get('expression'))
            if trigger.get('templateid'):
                father_host = mysqlapi.get('hosts', join='INNER JOIN items ON (items.hostid = hosts.hostid) INNER JOIN functions ON (functions.itemid = items.itemid)',
                        join_condition='functions.triggerid = {triggerid}'.format(triggerid=trigger.get('templateid')))
                dict['father_host'] = father_host.get('host')

            dict['trigger_id'] = trigger.get('triggerid')
            dict['priority'] = trigger.get('priority')
            dict['host'] = host.get('host')
            dict['description'] = trigger.get('description')
            dict['expression'] = trigger.get('expression')
            dict['status'] = trigger.get('status')
            dict['comments'] = trigger.get('comments')
            dict['father_node'] = node.name
            trigger_list.append(dict)

        trigger_json['trigger_list'] = trigger_list
        trigger_json['trigger_num'] = trigger_num
        trigger_json['page_num'] = page_num

    return JsonResponse(trigger_json)

@require_role(role="user")
def trigger_sync_zabbix(request):
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('node_id'))
            node = Zabbix.objects.get(id=node_id)
        except:
            return HttpResponse("同步数据异常！")
                        
        host_list = get_zabbix_host_list(node)
        template_list = get_zabbix_template_list(node)
        templateids = [template.get('templateid') for template in template_list]
        trigger_list = get_zabbix_trigger_list(node, templateids=templateids)

        for i in range(0, len(host_list), 200):
            hostids = [host.get('hostid') for host in host_list[i:i+200]]
            print(hostids)
            trigger_list += get_zabbix_trigger_list(node, hostids=hostids)
            time.sleep(1)
            print(len(trigger_list))
            print('host_list[%s]'% i)
        sync_trigger.delay(trigger_list, node_id)  # celery 任务

        return HttpResponse("同步触发器数据已完成！")
    else:
        return HttpResponse(None)

@require_role(role="user")
def trigger_add(request):
    if request.method == 'GET':
        print(request.GET)
        try:
            item_id = int(request.GET.get('itemid-db'))
            trigger_id = int(request.GET.get('triggerid'))
            node_id = int(request.GET.get('nodeid'))
            description = request.GET.get('description')
            expression = request.GET.get('expression')
            priority = int(request.GET.get('priority'))
            status = int(request.GET.get('status'))
            comments = request.GET.get('comments')
            exp_tmp = re.match("^\{(.*?)\}", expression).group(1)
            function_param = exp_tmp.split('.')[-1]
            res = re.findall(r'[^()]+', function_param)
            function = res[0]
            if len(res) >= 2:
                parameter = res[1]
            else:
                parameter = ''
        except:
            return HttpResponse(u'数据传输异常！')

        node = Zabbix.objects.get(id=node_id)
        if trigger_id == 0:  # 新增触发器
            create_result = create_zabbix_trigger(node, description, expression, priority, status, comments)
            if create_result.get('triggerids'):
                return HttpResponse(u'创建触发器[%s]成功。' % description)
            else:
                return HttpResponse(create_result.get('data'))
        else:  # 编辑触发器
            tri_dict = {
                "triggerid": trigger_id,
                "description": description,
                "expression": expression,
                "priority": priority,
                "status": status,
                "comments": comments,
            }
            result = update_zabbix_trigger(node, tri_dict)
            if result.get('triggerids'):
                return HttpResponse(u'修改触发器[%s]成功。' % description)
            else:
                return HttpResponse(result.get('data'))

@require_role(role="user")
def trigger_edit(request):
    trigger_json = {}
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('node_id'))
            trigger_id = int(request.POST.get('trigger_id'))
        except:
            print('get trigger info error!')
            return JsonResponse(trigger_json)

        node = Zabbix.objects.get(id=node_id)
        mysqlapi = Mysqlapi(user=node.zbx_mysql_user, password=node.zbx_mysql_passwd, db=node.zbx_mysql_db, host=node.zbx_mysql_host, port=node.zbx_mysql_port)
        trigger_obj = mysqlapi.get('triggers', triggerid=trigger_id)
        function_obj = mysqlapi.select('functions', triggerid=trigger_id)
        host = mysqlapi.get('hosts', join='INNER JOIN items ON (items.hostid = hosts.hostid) INNER JOIN functions ON (functions.itemid = items.itemid)',
                            join_condition='functions.triggerid={triggerid}'.format(triggerid=trigger_id))
        item = mysqlapi.get('items', join='INNER JOIN functions ON (functions.itemid = items.itemid)',
                            join_condition='functions.triggerid = {triggerid}'.format(triggerid=trigger_id))
        exp_str = "{%s:%s.%s(%s)}" % (host.get('host'), item.get('key_'), function_obj[0].get('function'), function_obj[0].get('parameter'))
        expression = re.sub("\{(.*?)\}", exp_str, trigger_obj.get('expression'))
        if trigger_obj.get('templateid'):
            father_host = mysqlapi.get('hosts', join='INNER JOIN items ON (items.hostid = hosts.hostid) INNER JOIN functions ON (functions.itemid = items.itemid)',
                            join_condition='functions.triggerid={triggerid}'.format(triggerid=trigger_obj.get('templateid')))
            trigger_json['father_tri_id'] = trigger_obj.get('templateid')
            trigger_json['father_name'] = father_host.get('host')
            trigger_json['father_id'] = father_host.get('hostid')

        trigger_json['expression'] = expression
        trigger_json['description'] = trigger_obj.get('description')
        trigger_json['status'] = trigger_obj.get('status')
        trigger_json['priority'] = trigger_obj.get('priority')
        trigger_json['comments'] = trigger_obj.get('comments')
        trigger_json['item_id'] = function_obj[0].get('itemid')

    return JsonResponse(trigger_json)

@require_role(role="user")
def trigger_del(request):
    msg = ''
    if request.method == 'POST':
        try:
            node_id = int(request.POST.get('node_id'))
            trigger_id = request.POST.get('trigger_id')

            if trigger_id:
                trigger_id_list = trigger_id.split(',')
            else:
                trigger_id_list = []

            node = Zabbix.objects.get(id=node_id)
            result = delete_zabbix_trigger(node, trigger_id_list)
            if result.get('triggerids'):
                msg = u'成功删除触发器！'
            elif result.get('data'):
                msg = result.get('data')
            else:
                msg = u'参数传递为空值！'
        except:
            msg = u'删除操作执行异常！'

    return HttpResponse(msg)
