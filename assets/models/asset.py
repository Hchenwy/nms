#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from django.db import models
from django.shortcuts import reverse
import logging
import uuid
from django.utils.translation import ugettext_lazy as _ 
from . import IDC, AssetGroup

__all__ = ['Asset']
logger = logging.getLogger(__name__)


class Asset(models.Model):
    STATUS_CHOICES = (
        ('In use', _('使用中')),
        ('Out of use', _('空闲中')),
    )
    TYPE_CHOICES = (
        ('Server', _('服务器')),
        ('Switch', _('交换机')),
    )
    ENV_CHOICES = (
        ('Prod', '生产环境'),
        ('Dev', '开发环境'),
        ('Test', '测试环境'),
    )

    # Important
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    ip = models.GenericIPAddressField(max_length=32, default="0.0.0.0", verbose_name=_('IP'), db_index=True)
    hostname = models.CharField(max_length=128, unique=True, verbose_name=_('资产名称'))
    groups = models.ManyToManyField(AssetGroup, blank=True, related_name='assets',
                                    verbose_name=_('资产组'))

    '''
    admin_user = models.ForeignKey(AdminUser, null=True, blank=True, related_name='assets',
                                   on_delete=models.SET_NULL, verbose_name=_("管理用户"))
    system_users = models.ManyToManyField(SystemUser, blank=True,
                                          related_name='assets',
                                          verbose_name=_("系统用户"))
    '''

    IDC = models.ForeignKey(IDC, blank=True, null=True, related_name='assets',
                            on_delete=models.SET_NULL, verbose_name=_('机房'),)
    monitor_id = models.IntegerField(null=True, blank=True, verbose_name=_('监控id'))
    is_active = models.BooleanField(default=True, verbose_name=_('激活'))
    type = models.CharField(choices=TYPE_CHOICES, max_length=16, blank=True, null=True,
                            default='Server', verbose_name=_('资产类型'),)
    env = models.CharField(choices=ENV_CHOICES, max_length=8, blank=True, null=True,
                           default='Prod', verbose_name=_('资产环境'),)
    status = models.CharField(choices=STATUS_CHOICES, max_length=12, null=True, blank=True,
                              default='In use', verbose_name=_('资产状态'))

    # Some information
    public_ip = models.GenericIPAddressField(max_length=32, blank=True,
                                             null=True, verbose_name=_('公网 IP'))
    remote_card_ip = models.CharField(max_length=16, null=True, blank=True,
                                      verbose_name=_('远程管理卡 IP'))
    cabinet_no = models.CharField(max_length=32, null=True, blank=True, verbose_name=_('机柜编号'))
    cabinet_pos = models.IntegerField(null=True, blank=True, verbose_name=_('机柜层号'))
    number = models.CharField(max_length=32, null=True, blank=True, verbose_name=_('资产编号'))

    # Collect
    vendor = models.CharField(max_length=64, null=True, blank=True, verbose_name=_('制造商'))
    model = models.CharField(max_length=54, null=True, blank=True, verbose_name=_('型号'))
    sn = models.CharField(max_length=128, null=True, blank=True, verbose_name=_('序列号'))

    cpu_model = models.CharField(max_length=64, null=True, blank=True, verbose_name=_('CPU型号'))
    cpu_count = models.IntegerField(null=True, blank=True, verbose_name=_('CPU数量'))
    cpu_cores = models.IntegerField(null=True, blank=True, verbose_name=_('CPU核数'))
    memory = models.CharField(max_length=64, null=True, blank=True, verbose_name=_('内存'))
    disk_total = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_('硬盘大小'))
    disk_info = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_('硬盘信息'))

    platform = models.CharField(max_length=128, null=True, blank=True, verbose_name=_('系统平台'))
    os = models.CharField(max_length=128, null=True, blank=True, verbose_name=_('操作系统'))
    os_version = models.CharField(max_length=16, null=True, blank=True, verbose_name=_('系统版本'))
    os_arch = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('系统架构'))

    created_by = models.CharField(max_length=32, null=True, blank=True, verbose_name=_('创建者'))
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_('创建日期'))
    comment = models.TextField(max_length=128, default='', blank=True, verbose_name=_('备注'))


    def __unicode__(self):
        return '%s <%s>' % (self.hostname, self.ip)
    __str__ = __unicode__

    def get_absolute_url(self):
        return reverse('assets:asset-detail', args=(self.pk,))

    @property
    def is_valid(self):
        warning = ''
        if not self.is_active:
            warning += ' inactive'
        else:
            return True, ''
        return False, warning


    @classmethod
    def generate_fake(cls, count=100):
        from random import seed, choice
        import forgery_py
        from django.db import IntegrityError

        seed()
        for i in range(count):
            asset = cls(ip='%s.%s.%s.%s' % (i, i, i, i),
                        hostname=forgery_py.internet.user_name(True),
                        #admin_user=choice(AdminUser.objects.all()),
                        IDC=choice(IDC.objects.all()),
                        created_by='Fake')
            try:
                asset.save()
                #asset.system_users = [choice(SystemUser.objects.all()) for i in range(3)]
                asset.groups = [choice(AssetGroup.objects.all()) for i in range(3)]
                logger.debug('Generate fake asset : %s' % asset.ip)
            except IntegrityError:
                print('Error continue')
                continue