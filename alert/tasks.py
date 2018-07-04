#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from zabbix.models import *
from zabbix.zbx_api import get_zabbix_alert
from celery import task

def sync_alert(list, node_id):
    new_alert_id = []
    old_alert_list = Triggers.objects.filter(node_id=node_id, value=1)

    ''' 更新最新的告警项 '''
    for trigger in list:
        new_alert_id.append(int(trigger.get('triggerid')))
        Triggers.objects.filter(node_id=node_id, triggerid=int(trigger.get('triggerid'))).update(value=1, lastchange=trigger['lastchange'])

    ''' 重置已经解决的告警项 '''
    for old_alert in old_alert_list:
        if old_alert.triggerid not in new_alert_id:
            old_alert.value = 0
            old_alert.save()

    return True

@task
def sync_all_alert():
    node_list = Zabbix.objects.all()
    for node in node_list:
        alert_list = get_zabbix_alert(node)
        sync_alert(alert_list, node.id)

