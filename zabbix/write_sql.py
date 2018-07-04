#!/usr/bin/env python
# -*- coding: utf-8 -*-

def write_host_tbl(host, node_id=None, proxy_hostid=None, maintenanceid=None, templateid=None):
    data = {
        'node_id': node_id,
        'hostid': int(host.get('hostid')),
        'proxy_hostid': proxy_hostid,
        'host': host.get('host'),
        'status': int(host.get('status')),
        'disable_until': int(host.get('disable_until')),
        'error': host.get('error'),
        'available': int(host.get('available')),
        'errors_from': int(host.get('errors_from')),
        'lastaccess': int(host.get('lastaccess')),
        'ipmi_authtype': int(host.get('ipmi_authtype')),
        'ipmi_privilege': int(host.get('ipmi_privilege')),
        'ipmi_username': host.get('ipmi_username'),
        'ipmi_password': host.get('ipmi_password'),
        'ipmi_disable_until': int(host.get('ipmi_disable_until')),
        'ipmi_available': int(host.get('ipmi_available')),
        'snmp_disable_until': int(host.get('snmp_disable_until')),
        'snmp_available': int(host.get('snmp_available')),
        'maintenanceid': maintenanceid,
        'maintenance_status': int(host.get('maintenance_status')),
        'maintenance_type': int(host.get('maintenance_type')),
        'maintenance_from': int(host.get('maintenance_from')),
        'ipmi_errors_from': int(host.get('ipmi_errors_from')),
        'snmp_errors_from': int(host.get('snmp_errors_from')),
        'ipmi_error': host.get('ipmi_error'),
        'snmp_error': host.get('snmp_error'),
        'jmx_disable_until': int(host.get('jmx_disable_until')),
        'jmx_available': int(host.get('jmx_available')),
        'jmx_errors_from': int(host.get('jmx_errors_from')),
        'jmx_error': host.get('jmx_error'),
        'name': host.get('name'),
        'flags': int(host.get('flags')),
        'templateid': templateid,
        'description': host.get('description'),
        'tls_connect': int(host.get('tls_connect')),
        'tls_accept': int(host.get('tls_accept')),
        'tls_issuer': host.get('tls_issuer'),
        'tls_subject': host.get('tls_subject'),
        'tls_psk_identity': host.get('tls_psk_identity'),
        'tls_psk': host.get('tls_psk'),
    }
    return data

def write_template_tbl(host, node_id=None, proxy_hostid=None, maintenanceid=None, templateid=None):
    data = {
        'node_id': node_id,
        'hostid': int(host.get('templateid')),
        'proxy_hostid': proxy_hostid,
        'host': host.get('host'),
        'status': int(host.get('status')),
        'disable_until': int(host.get('disable_until')),
        'error': host.get('error'),
        'available': int(host.get('available')),
        'errors_from': int(host.get('errors_from')),
        'lastaccess': int(host.get('lastaccess')),
        'ipmi_authtype': int(host.get('ipmi_authtype')),
        'ipmi_privilege': int(host.get('ipmi_privilege')),
        'ipmi_username': host.get('ipmi_username'),
        'ipmi_password': host.get('ipmi_password'),
        'ipmi_disable_until': int(host.get('ipmi_disable_until')),
        'ipmi_available': int(host.get('ipmi_available')),
        'snmp_disable_until': int(host.get('snmp_disable_until')),
        'snmp_available': int(host.get('snmp_available')),
        'maintenanceid': maintenanceid,
        'maintenance_status': int(host.get('maintenance_status')),
        'maintenance_type': int(host.get('maintenance_type')),
        'maintenance_from': int(host.get('maintenance_from')),
        'ipmi_errors_from': int(host.get('ipmi_errors_from')),
        'snmp_errors_from': int(host.get('snmp_errors_from')),
        'ipmi_error': host.get('ipmi_error'),
        'snmp_error': host.get('snmp_error'),
        'jmx_disable_until': int(host.get('jmx_disable_until')),
        'jmx_available': int(host.get('jmx_available')),
        'jmx_errors_from': int(host.get('jmx_errors_from')),
        'jmx_error': host.get('jmx_error'),
        'name': host.get('name'),
        'flags': int(host.get('flags')),
        'templateid': templateid,
        'description': host.get('description'),
        'tls_connect': int(host.get('tls_connect')),
        'tls_accept': int(host.get('tls_accept')),
        'tls_issuer': host.get('tls_issuer'),
        'tls_subject': host.get('tls_subject'),
        'tls_psk_identity': host.get('tls_psk_identity'),
        'tls_psk': host.get('tls_psk'),
    }
    return data

def write_interface_tbl(interface, node_id=None, hostid=None):
    data = {
        'node_id': node_id,
        'interfaceid': interface.get('interfaceid'),
        'hostid': hostid,
        'main': int(interface.get('main')),
        'type': int(interface.get('type')),
        'useip': int(interface.get('useip')),
        'ip': interface.get('ip'),
        'dns': interface.get('dns'),
        'port': interface.get('port'),
        'bulk': int(interface.get('bulk')),
    }
    return data

def write_hostsgroup_tbl(hostsgroup, node_id=None, hostid=None, groupid=None):
    data = {
        'groupid': groupid,
        'node_id': node_id,
        'hostid': hostid,
    }
    return data

def write_group_tbl(group, node_id=None):
    data = {
        'node_id': node_id,
        'groupid': int(group.get('groupid')),
        'name': group.get('name'),
        'internal': int(group.get('internal')),
        'flags': int(group.get('flags')),
    }
    return data

def write_item_tbl(item, node_id=None, hostid=None, interfaceid=None, master_itemid=None, templateid=None, valuemapid=None):
    data = {
        'node_id': node_id,
        'itemid':int(item.get('itemid') or '0'),
        'type': int(item.get('type') or '0'),
        'snmp_community': item.get('snmp_community') or '',
        'snmp_oid': item.get('snmp_oid') or '',
        'name': item.get('name') or '',
        'key_field': item.get('key_') or '',
        'delay': item.get('delay') or '0',
        'history': item.get('history') or '90d',
        'trends': item.get('trends') or '365d',
        'status': int(item.get('status') or '0'),
        'value_type': int(item.get('value_type') or '0'),
        'trapper_hosts': item.get('trapper_hosts') or '',
        'units': item.get('units') or '',
        'snmpv3_securityname': item.get('snmpv3_securityname') or '',
        'snmpv3_securitylevel': int(item.get('snmpv3_securitylevel') or '0'),
        'snmpv3_authpassphrase': item.get('snmpv3_authpassphrase') or '',
        'snmpv3_privpassphrase': item.get('snmpv3_privpassphrase') or '',
        'formula': item.get('formula') or '',
        'error': item.get('error') or '',
        'lastlogsize': int(item.get('lastlogsize') or '0'),
        'logtimefmt': item.get('logtimefmt') or '',
        'params': item.get('params') or '',
        'ipmi_sensor': item.get('ipmi_sensor') or '',
        'authtype': int(item.get('authtype') or '0'),
        'username': item.get('username') or '',
        'password': item.get('password') or '',
        'publickey': item.get('publickey') or '',
        'privatekey': item.get('privatekey') or '',
        'mtime': int(item.get('mtime') or '0'),
        'flags': int(item.get('flags') or '0'),
        'port': item.get('port') or '',
        'description': item.get('description') or '',
        'inventory_link': int(item.get('inventory_link') or '0'),
        'lifetime': item.get('lifetime') or '30d',
        'snmpv3_authprotocol': int(item.get('snmpv3_authprotocol') or '0'),
        'snmpv3_privprotocol': int(item.get('snmpv3_privprotocol') or '0') ,
        'state': int(item.get('state') or '0'),
        'snmpv3_contextname': item.get('snmpv3_contextname') or '',
        'evaltype': int(item.get('evaltype') or '0'),
        'jmx_endpoint': item.get('jmx_endpoint') or '',
        #'hostid': None,
        #'interfaceid': None,
        #'master_itemid': None,
        #'templateid': None,
        #'valuemapid': None,
    }
    return data

def write_trigger_tbl(trigger, node_id=None, templateid=None):
    data = {
        'node_id': node_id,
        'triggerid': int(trigger.get('triggerid')),
        'expression': trigger.get('expression') or '',
        'description': trigger.get('description') or '',
        'url': trigger.get('url') or '',
        'status': int(trigger.get('status') or '0'),
        'value': int(trigger.get('value') or '0'),
        'priority': int(trigger.get('priority') or '0'),
        'lastchange': int(trigger.get('lastchange') or '0'),
        'comments': trigger.get('comments') or '',
        'error': trigger.get('error') or '',
        'type': int(trigger.get('type') or '0'),
        'state': int(trigger.get('state') or '0'),
        'flags': int(trigger.get('flags') or '0'),
        'recovery_mode': int(trigger.get('recovery_mode') or '0'),
        'recovery_expression': trigger.get('recovery_expression') or '',
        'correlation_mode': int(trigger.get('correlation_mode') or '0'),
        'correlation_tag': trigger.get('correlation_tag') or '',
        'manual_close': int(trigger.get('manual_close') or '0'),
        'templateid': templateid,
    }
    return data

def write_functions_tbl(functions, node_id=None, itemid=None, triggerid=None):
    data = {
        'node_id': node_id,
        'functionid': int(functions.get('functionid')),
        'function': functions.get('function'),
        'parameter': functions.get('parameter'),
        'itemid': itemid,
        'triggerid': triggerid,
    }
    return data
