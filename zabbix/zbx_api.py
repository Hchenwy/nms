#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import urllib.request
import urllib.parse
from django.utils import timezone

class ZabbixAPI(object):
    def __init__(self,url,user,password,headers = {"Content-Type":"application/json"}):
        self.request_data = {
            "jsonrpc":"2.0",
            "method":"user.login",
            "params":"null",
            "id": 1,
        }
        self.url = url
        self.headers = headers
        self.login(user,password)

    def login(self,user,password):
        method = "user.login"
        params = {"user":user,"password":password}
        auth = self.deal_request(method=method,params=params)
        self.request_data["auth"] = auth

    def deal_request(self,method,params):
        self.request_data["method"] = method
        self.request_data["params"] = params
        self.data = bytes(json.dumps(self.request_data), 'utf8')
        request = urllib.request.Request(url=self.url,data=self.data,headers=self.headers)
        try:
            response = urllib.request.urlopen(request, timeout=60)
            s = json.loads(response.read().decode('utf-8'))
            return s["result"]
        except:
            response = urllib.request.urlopen(request)
            s = json.loads(response.read().decode('utf-8'))
            print ("Error: zapi 001")
            return s["error"]

    def __getattr__(self, name):
        return ZabbixObj(name, self)

class ZabbixObj(object):

    def __init__(self,method_fomer,ZabbixAPI):
        self.method_fomer = method_fomer
        self.ZabbixAPI = ZabbixAPI

    def __getattr__(self, name):
        def func(params):
            method = self.method_fomer+"."+name
            params = params
            return  self.ZabbixAPI.deal_request(method=method,params=params)
        return func

''' 获取zabbix数据库主机列表 '''
def get_zabbix_host_list(node):
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        try:
            host_list = zapi.host.get({"output": ["status", "host", "available"], "selectInterfaces": "extend"})
            node.zbx_total = len(host_list)
            node.check_time = timezone.now()
            node.zbx_status = 1
            node.save()
            return host_list
        except:
            node.check_time = timezone.now()
            node.zbx_status = 2
            node.save()
            return False
    else:
        return False

def get_zabbix_group_list(node):
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        try:
            hostsgroup_list = zapi.host.get({"output": ["hostid"],
                                       "selectGroups": ["groupid"]
                                       })
            tempgroup_list = zapi.template.get({"output": ["hostid"],
                                       "selectGroups": ["groupid"]
                                       })
            return hostsgroup_list, tempgroup_list
        except:
            return False
    else:
        return False

def get_zabbix_template_list(node):
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        try:
            template_list = zapi.template.get({"output": ["host", "description", "status"]})
            return template_list
        except:
            return False
    else:
        return False

def get_zabbix_item(zapi, **kwargs):
    try:
        param_dict = {"output": ["hostid", "name", "type", "key_", "value_type", "units", "status", "description", "delay", "templateid"]}
        for key in kwargs:
            if key == 'hostids':
                param_dict['hostids'] = kwargs[key]
            elif key == 'templateids':
                param_dict['templateids'] = kwargs[key]
        item_list = zapi.item.get(param_dict)
        return item_list
    except:
        return []

def get_zabbix_items_list(node, **kwargs):
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        item_list = []
        try:
            param_dict = {"output": ["hostid", "name", "type", "key_", "value_type", "units", "status", "description", "delay", "templateid"]}
            for key in kwargs:
                if key == 'hostids':
                    param_dict['hostids'] = kwargs[key]
                elif key == 'templateids':
                    param_dict['templateids'] = kwargs[key]

            item_list = zapi.item.get(param_dict)
            return item_list
        except:
            print('get_zabbix_items_list fail')
            return False
    else:
        print ('zabbix user information is error!')
        return False

def get_zabbix_trigger(zapi, **kwargs):
    try:
        param_dict = {"output": "extend", "selectFunctions": "extend"}
        for key in kwargs:
            if key == 'hostids':
                param_dict['hostids'] = kwargs[key]
            elif key == 'templateids':
                param_dict['templateids'] = kwargs[key]

        trigger_list = zapi.trigger.get(param_dict)
        return trigger_list
    except:
        print('get_zabbix_trigger error')
        return []

def get_zabbix_trigger_list(node, **kwargs):
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        trigger_list = []
        try:
            param_dict = {"output": ["triggerid", "expression", "description", "status", "priority", "lastchange", "templateid", "value"], "selectFunctions": "extend"}
            for key in kwargs:
                if key == 'hostids':
                    param_dict['hostids'] = kwargs[key]
                elif key == 'templateids':
                    param_dict['templateids'] = kwargs[key]

            trigger_list = zapi.trigger.get(param_dict)
            return trigger_list
        except:
            print ('get_zabbix_trigger_list fail!')
            return False
    else:
        print ('zabbix user information is error!')
        return False

def get_zabbix_alert(node):
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        try:
            param_dict = {"output": ["triggerid", "lastchange"], "filter": {"value": 1}}
            trigger_list = zapi.trigger.get(param_dict)
            return trigger_list
        except:
            print ('get_zabbix_alert fail!')
            return False
    else:
        print ('zabbix user information is error!')
        return False

def create_zabbix_trigger(node, description=None, expression=None, priority='', status='', comments=''):
    if not description or not expression:
        print('Incorrect description or expression.')
        return False
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        try:
            create_result = zapi.trigger.create({"description": description,
                                                "expression": expression,
                                                "priority": priority,
                                                "status": status,
                                                "comments": comments,
                                              })
            return create_result
        except:
            print ('create_zabbix_trigger fail!')
            return False
    else:
        print ('zabbix user information is error!')
        return False

def update_zabbix_trigger(node, trigger_dict={}):
    if not trigger_dict:
        print('Incorrect input trigger_dict.')
        return False
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        try:
            update_result = zapi.trigger.update(trigger_dict)
            return update_result
        except:
            print ('update_zabbix_trigger fail!')
            return False
    else:
        print ('zabbix user information is error!')
        return False

def delete_zabbix_trigger(node, triggerid=[]):
    if not triggerid:
        print('Empty input triggerid_list!')
        return False
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        try:
            delete_result = zapi.trigger.delete(triggerid)
            return delete_result
        except:
            print ('delete_zabbix_trigger fail!')
            return False
    else:
        print ('zabbix user information is error!')
        return False

def create_zabbix_item(node, param_dict):
    if param_dict.get('delay') == '' or param_dict.get('key_') == '' or param_dict.get('name') == '':
        print('Empty parameter name, key_ or delay.')
        return False
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        try:
            create_result = zapi.item.create(param_dict)
            return create_result
        except:
            print ('create_zabbix_item fail!')
            return False
    else:
        print ('zabbix user information is error!')
        return False

def update_zabbix_item(node, param_dict):
    if param_dict.get('delay') == '' or param_dict.get('key_') == '' or param_dict.get('name') == '':
        print('Empty parameter name, key_ or delay.')
        return False
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        try:
            result = zapi.item.update(param_dict)
            return result
        except:
            print ('update_zabbix_item fail!')
            return False
    else:
        print ('zabbix user information is error!')
        return False

def delete_zabbix_item(node, item_id_list=[]):
    if not item_id_list:
        print('Empty input item_id_list!')
        return False
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        try:
            result = zapi.item.delete(item_id_list)
            return result
        except:
            print ('delete_zabbix_item fail!')
            return False
    else:
        print ('zabbix user information is error!')
        return False

def create_zabbix_host(node, type= '', host='', status='0', ip='', port='', usemacro=[]):
    if not host or not ip or not port or not type:
        print('Incorrect host or ip or port or type.')
        return False
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        try:
            groupid_result = zapi.hostgroup.get({"output": ["groupid"], "limit": 1})
            try:
                groupid = groupid_result[0].get('groupid')
            except:
                groupid_result = zapi.hostgroup.create({"name": "NMS default"})
                groupid = groupid_result.get('groupids')[0]

            param_dict = {"host": host, "status": status, "interfaces": [{"type": type,"ip": ip,"port": port,"main": 1,"useip": 1,"dns": ""}],
                            "groups": [{"groupid": groupid}]}
            if usemacro:
                param_dict['macros'] = usemacro

            print(param_dict)
            result = zapi.host.create(param_dict)
            return result
        except:
            print ('create_zabbix_host fail!')
            return False
    else:
        print ('zabbix user information is error!')
        return False

def update_zabbix_host(node, hostid='', type= '', host='', status='0', ip='', port='', usemacro=[]):
    if not hostid or not host or not ip or not port or not type:
        print('Incorrect hostid or host or ip or port or type.')
        return False
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        try:
            param_dict = {"hostid": hostid, "host": host, "status": status, "interfaces": [{"type": type, "ip": ip, "port": port, "main": 1, "useip": 1, "dns": ""}]}
            if usemacro:
                param_dict['macros'] = usemacro

            print(param_dict)
            result = zapi.host.update(param_dict)
            return result
        except:
            print ('update_zabbix_host fail!')
            return False
    else:
        print ('zabbix user information is error!')
        return False

def delete_zabbix_host(node, host_id_list=[]):
    if not host_id_list:
        print('Empty input host_id_list.')
        return False
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        try:
            result = zapi.host.delete(host_id_list)
            return result
        except:
            print ('delete_zabbix_host fail!')
            return False
    else:
        print ('zabbix user information is error!')
        return False

def create_zabbix_template(node, host='', descripation='', hosts=[]):
    if not host:
        print('Incorrect input host.')
        return False
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        try:
            groupid_result = zapi.hostgroup.get({"output": ["groupid"], "limit": 1})
            try:
                groupid = groupid_result[0].get('groupid')
            except:
                groupid_result = zapi.hostgroup.create({"name": "NMS default"})
                groupid = groupid_result.get('groupids')[0]

            param_dict = {"host": host, "description": descripation, "groups": [{"groupid": groupid}]}
            if hosts:
                param_dict['hosts'] = hosts

            print(param_dict)
            result = zapi.template.create(param_dict)
            return result
        except:
            print ('create_zabbix_template fail!')
            return False
    else:
        print ('zabbix user information is error!')
        return False

def update_zabbix_template(node, template_id='', host='', descripation='', hosts=[]):
    if not host or not template_id:
        print('Empty input host or template_id.')
        return False
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        try:
            param_dict = {"host": host, "description": descripation, "templateid": template_id, "hosts": hosts}
            print(param_dict)
            result = zapi.template.update(param_dict)
            return result
        except:
            print ('update_zabbix_template fail!')
            return False
    else:
        print ('zabbix user information is error!')
        return False

def delete_zabbix_template(node, template_id_list=[]):
    if not template_id_list:
        print('Empty input template_id_list.')
        return False
    if node.zbx_url and node.zbx_url != '' and node.zbx_user and node.zbx_user != '' and node.zbx_passwd and node.zbx_passwd != '':
        zapi = ZabbixAPI(node.zbx_url, node.zbx_user, node.zbx_passwd)
        try:
            result = zapi.template.delete(template_id_list)
            return result
        except:
            print ('delete_zabbix_template fail!')
            return False
    else:
        print ('zabbix user information is error!')
        return False













