#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 

from __future__ import unicode_literals


from django.shortcuts import reverse
from django.db import models
import logging
import uuid
from django.utils.translation import ugettext_lazy as _


__all__ = ['AssetGroup']
logger = logging.getLogger(__name__)


class AssetGroup(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=64, unique=True, verbose_name=_('名称'))
    created_by = models.CharField(max_length=32, blank=True, verbose_name=_('创建者'))
    date_created = models.DateTimeField(auto_now_add=True, null=True, verbose_name=_('创建日期'))
    comment = models.TextField(blank=True, verbose_name=_('备注'))

    def __unicode__(self):
        return self.name
    __str__ = __unicode__

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('assets:asset-group-detail', args=(self.pk,))

    @classmethod
    def initial(cls):
        asset_group = cls(name=_('默认'), comment=_('默认主机组'))
        asset_group.save()

    @classmethod
    def generate_fake(cls, count=100):
        from random import seed
        import forgery_py
        from django.db import IntegrityError
        groups = ["存储节点", "管理节点", "计算节点", "Web", "数据库", "测试", "研发", "商用"]

        seed()
        for i in groups:
            group = cls(name=groups[groups.index(i)],
                        comment=forgery_py.lorem_ipsum.sentence(),
                        created_by='Fake')
            try:
                group.save()
                logger.debug('Generate fake asset group: %s' % group.name)
            except IntegrityError:
                print('Error continue')
                continue