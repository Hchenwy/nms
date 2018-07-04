#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

STATUS = (
    (1, _("online")),
    (2, _("offline")),
    (3, _("unknow"))
)

Resolve_Status = (
    (0, u"恢复"),
    (1, u"故障"),
    (2, u"未知")
)

class Zabbix(models.Model):
    name = models.CharField(max_length=32, verbose_name=_('name'))
    bandwidth = models.CharField(max_length=32, blank=True, null=True, default='', verbose_name=_('bandwidth'))
    contacts = models.CharField(max_length=16, blank=True, null=True, default='', verbose_name=_('contacts'))
    phone = models.CharField(max_length=32, blank=True, null=True, default='', verbose_name=_('phone'))
    address = models.CharField(max_length=128, blank=True, null=True, default='', verbose_name=_('address'))
    zbx_ip = models.CharField(max_length=64, blank=True, verbose_name=_('zabbix ipaddress'))
    zbx_url = models.CharField(max_length=64, blank=True, verbose_name=_('zabbix URL'))
    zbx_user = models.CharField(max_length=64, blank=True, verbose_name=_('zabbix api user name'))
    zbx_passwd = models.CharField(max_length=64, blank=True, verbose_name=_('zabbix api password'))
    zbx_mysql_user = models.CharField(max_length=64, blank=True, default='', verbose_name=_('zabbix mysql user'))
    zbx_mysql_passwd = models.CharField(max_length=64, blank=True, default='', verbose_name=_('zabbix mysql password'))
    zbx_mysql_db = models.CharField(max_length=64, blank=True, default='', verbose_name=_('zabbix mysql password'))
    zbx_mysql_host = models.CharField(max_length=64, blank=True, default='127.0.0.1', verbose_name=_('zabbix mysql password'))
    zbx_mysql_port = models.CharField(max_length=64, default='3306', blank=True, verbose_name=_('zabbix mysql port'))
    zbx_status = models.IntegerField(choices=STATUS,  blank=True, null=True, default=2, verbose_name=_('zabbix status'))
    zbx_total = models.IntegerField(blank=True, null=True, verbose_name=_('zabbix hosts total'))
    zbx_danger = models.IntegerField(blank=True, null=True, verbose_name=_('zabbix danger number'))
    zbx_warning = models.IntegerField(blank=True, null=True, verbose_name=_('zabbix warning number'))
    check_time = models.DateTimeField(blank=True, null=True, verbose_name=_('last chkeck time'))
    date_added = models.DateField(auto_now=True, null=True, verbose_name=_('add date'))
    operator = models.CharField(max_length=32, blank=True, default='', null=True, verbose_name=_(''))
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=_('comment'))
    alive = models.IntegerField(choices=STATUS,  blank=True, null=True, default=2, verbose_name=_('alive'))

    def __unicode__(self):
        return self.name
    __str__ = __unicode__

class Maintenances(models.Model):
    node = models.ForeignKey(Zabbix, blank=True, null=True, on_delete=models.SET_NULL, db_column='node_id', verbose_name=u"所属节点")
    maintenanceid = models.BigIntegerField()
    name = models.CharField(unique=True, max_length=128)
    maintenance_type = models.IntegerField()
    description = models.TextField()
    active_since = models.IntegerField()
    active_till = models.IntegerField()

    def __unicode__(self):
        return self.maintenanceid
    __str__ = __unicode__


class Hosts(models.Model):
    up_time = models.IntegerField(default=0)
    node = models.ForeignKey(Zabbix, blank=True, null=True, on_delete=models.SET_NULL, db_column='node_id', verbose_name=u"所属节点")
    hostid = models.BigIntegerField(verbose_name=u"主机或模板ID")
    proxy_hostid = models.ForeignKey('self', related_name= "hosts1", on_delete=models.DO_NOTHING, db_column='proxy_hostid', blank=True, null=True, verbose_name=u"代理主机ID")
    host = models.CharField(max_length=128, verbose_name=u"主机或模板名称", default='')
    status = models.IntegerField(blank=True, null=True, verbose_name=u"主机状态", default=0) # 0=enable； 1=disabled； 3=template
    disable_until = models.IntegerField(default=0)
    error = models.CharField(max_length=2048, default='')
    available = models.IntegerField(verbose_name=u"客户端状态", default=0)
    errors_from = models.IntegerField(default=0)
    lastaccess = models.IntegerField(default=0)
    ipmi_authtype = models.IntegerField(default=-1)
    ipmi_privilege = models.IntegerField(default=2)
    ipmi_username = models.CharField(max_length=16, default='')
    ipmi_password = models.CharField(max_length=20, default='')
    ipmi_disable_until = models.IntegerField(default=0)
    ipmi_available = models.IntegerField(default=0)
    snmp_disable_until = models.IntegerField(default=0)
    snmp_available = models.IntegerField(default=0)
    maintenanceid = models.ForeignKey(Maintenances, db_column='maintenanceid', on_delete=models.DO_NOTHING, blank=True,null=True)
    maintenance_status = models.IntegerField(default=0)
    maintenance_type = models.IntegerField(default=0)
    maintenance_from = models.IntegerField(default=0)
    ipmi_errors_from = models.IntegerField(default=0)
    snmp_errors_from = models.IntegerField(default=0)
    ipmi_error = models.CharField(max_length=2048, default='')
    snmp_error = models.CharField(max_length=2048, default='')
    jmx_disable_until = models.IntegerField(default=0)
    jmx_available = models.IntegerField(default=0)
    jmx_errors_from = models.IntegerField(default=0)
    jmx_error = models.CharField(max_length=2048, default='')
    name = models.CharField(max_length=128, default='')
    flags = models.IntegerField(default=0)
    templateid = models.ForeignKey('self', related_name= "hosts2", db_column='templateid', on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(default='')
    tls_connect = models.IntegerField(default=1)
    tls_accept = models.IntegerField(default=1)
    tls_issuer = models.CharField(max_length=1024, default='')
    tls_subject = models.CharField(max_length=1024, default='')
    tls_psk_identity = models.CharField(max_length=128, default='')
    tls_psk = models.CharField(max_length=512, default='')

    def __unicode__(self):
        return str(self.hostid)
    __str__ = __unicode__

class Hostmacro(models.Model):
    hostid = models.ForeignKey('Hosts', models.DO_NOTHING, db_column='hostid')
    macro = models.CharField(max_length=255, default='')
    value = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return str(self.hostid)
    __str__ = __unicode__

class Hoststemplates(models.Model):
    hostid = models.ForeignKey(Hosts, related_name="ht_host", on_delete=models.DO_NOTHING, db_column='hostid', blank=True, null=True)
    templateid = models.ForeignKey(Hosts, related_name="ht_template", on_delete=models.DO_NOTHING, db_column='templateid', blank=True, null=True)

    def __unicode__(self):
        return str(self.hostid)
    __str__ = __unicode__

class Groups(models.Model):
    node = models.ForeignKey(Zabbix, blank=True, null=True, on_delete=models.SET_NULL, db_column='node_id', verbose_name=u"所属节点")
    parentid = models.ForeignKey('self', db_column='parentid', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    internal = models.IntegerField()
    flags = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.name
    __str__ = __unicode__

class Hostsgroups(models.Model):
    hostid = models.ForeignKey(Hosts, models.DO_NOTHING, db_column='hostid', blank=True, null=True)
    groupid = models.ForeignKey(Groups, models.DO_NOTHING, db_column='groupid', blank=True, null=True)

class Valuemaps(models.Model):
    node = models.ForeignKey(Zabbix, blank=True, null=True, on_delete=models.SET_NULL, db_column='node_id', verbose_name=u"所属节点")
    valuemapid = models.BigIntegerField()
    name = models.CharField(unique=True, max_length=64)

    def __unicode__(self):
        return self.valuemapid
    __str__ = __unicode__


class Interface(models.Model):
    node = models.ForeignKey(Zabbix, blank=True, null=True, on_delete=models.SET_NULL, db_column='node_id', verbose_name=u"所属节点")
    interfaceid = models.BigIntegerField(default=0)
    hostid = models.ForeignKey(Hosts, on_delete=models.CASCADE, db_column='hostid', blank=True, null=True)
    main = models.IntegerField(default=1)
    type = models.IntegerField(default=1)
    useip = models.IntegerField(default=1)
    ip = models.CharField(max_length=64, default='127.0.0.1')
    dns = models.CharField(max_length=64, default='')
    port = models.CharField(max_length=64, default='10050')
    bulk = models.IntegerField(default=1)

    def __unicode__(self):
        return str(self.interfaceid)
    __str__ = __unicode__


class Items(models.Model):
    up_time = models.IntegerField(default=0)
    node = models.ForeignKey(Zabbix, blank=True, null=True, on_delete=models.SET_NULL, db_column='node_id', verbose_name=u"所属节点")
    itemid = models.BigIntegerField()
    type = models.IntegerField(default=0)
    snmp_community = models.CharField(max_length=64, default='')
    snmp_oid = models.CharField(max_length=512, default='')
    hostid = models.ForeignKey(Hosts, db_column='hostid', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, default='')
    key_field = models.CharField(db_column='key_', max_length=255, default='')  # Field renamed because it ended with '_'.
    delay = models.CharField(max_length=1024, default=0)
    history = models.CharField(max_length=255, default='90d')
    trends = models.CharField(max_length=255, default='365d')
    status = models.IntegerField(default=0)
    value_type = models.IntegerField(default=0)
    trapper_hosts = models.CharField(max_length=255, default='')
    units = models.CharField(max_length=255, default='')
    snmpv3_securityname = models.CharField(max_length=64, default='')
    snmpv3_securitylevel = models.IntegerField(default=0)
    snmpv3_authpassphrase = models.CharField(max_length=64, default='')
    snmpv3_privpassphrase = models.CharField(max_length=64, default='')
    formula = models.CharField(max_length=255, default='')
    error = models.CharField(max_length=2048, default='')
    lastlogsize = models.BigIntegerField(default=0)
    logtimefmt = models.CharField(max_length=64, default='')
    templateid = models.ForeignKey('self', related_name= "items1", on_delete=models.CASCADE, db_column='templateid', blank=True, null=True)
    valuemapid = models.ForeignKey(Valuemaps, on_delete=models.DO_NOTHING, db_column='valuemapid', blank=True, null=True)
    params = models.TextField(default='')
    ipmi_sensor = models.CharField(max_length=128, default='')
    authtype = models.IntegerField(default=0)
    username = models.CharField(max_length=64, default='')
    password = models.CharField(max_length=64, default='')
    publickey = models.CharField(max_length=64, default='')
    privatekey = models.CharField(max_length=64, default='')
    mtime = models.IntegerField(default=0)
    flags = models.IntegerField(default=0)
    interfaceid = models.ForeignKey(Interface, on_delete=models.DO_NOTHING, db_column='interfaceid', blank=True, null=True)
    port = models.CharField(max_length=64, default='')
    description = models.TextField(default='')
    inventory_link = models.IntegerField(default=0)
    lifetime = models.CharField(max_length=255, default='30d')
    snmpv3_authprotocol = models.IntegerField(default=0)
    snmpv3_privprotocol = models.IntegerField(default=0)
    state = models.IntegerField(default=0)
    snmpv3_contextname = models.CharField(max_length=255, default='')
    evaltype = models.IntegerField(default=0)
    jmx_endpoint = models.CharField(max_length=255, default='')
    master_itemid = models.ForeignKey('self',  related_name= "items2", on_delete=models.CASCADE, db_column='master_itemid', blank=True, null=True)

    def __unicode__(self):
        return str(self.itemid)
    __str__ = __unicode__

class Itemskey(models.Model):
    key = models.CharField(max_length=255, default='')
    description = models.CharField(max_length=255, default='')
    type = models.IntegerField()

class Triggers(models.Model):
    up_time = models.IntegerField(default=0)
    node = models.ForeignKey(Zabbix, blank=True, null=True, on_delete=models.SET_NULL, db_column='node_id', verbose_name=u"所属节点")
    triggerid = models.BigIntegerField(default=0)
    expression = models.CharField(max_length=2048, default='')
    description = models.CharField(max_length=255, default='')
    url = models.CharField(max_length=255, default='')
    status = models.IntegerField(default=0)
    value = models.IntegerField(default=0)
    priority = models.IntegerField(default=0)
    lastchange = models.IntegerField(default=0)
    comments = models.TextField(default='')
    error = models.CharField(max_length=2048, default='')
    templateid = models.ForeignKey('self', models.DO_NOTHING, db_column='templateid', blank=True, null=True)
    type = models.IntegerField(default=0)
    state = models.IntegerField(default=0)
    flags = models.IntegerField(default=0)
    recovery_mode = models.IntegerField(default=0)
    recovery_expression = models.CharField(max_length=2048, default='')
    correlation_mode = models.IntegerField(default=0)
    correlation_tag = models.CharField(max_length=255, default='')
    manual_close = models.IntegerField(default=0)

    def __unicode__(self):
        return str(self.triggerid)
    __str__ = __unicode__

class Functions(models.Model):
    node = models.ForeignKey(Zabbix, blank=True, null=True, on_delete=models.SET_NULL, db_column='node_id', verbose_name=u"所属节点")
    functionid = models.BigIntegerField(default=0)
    itemid = models.ForeignKey(Items, blank=True, null=True, on_delete=models.DO_NOTHING, db_column='itemid')
    triggerid = models.ForeignKey(Triggers, blank=True, null=True, on_delete=models.DO_NOTHING, db_column='triggerid')
    function = models.CharField(max_length=12, default='')
    parameter = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return str(self.functionid)
    __str__ = __unicode__

