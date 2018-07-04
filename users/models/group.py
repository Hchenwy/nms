# -*- coding: utf-8 -*-
'''用户组模块'''
import uuid

from django.shortcuts import reverse
from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _
from common.mixins import NoDeleteModelMixin

class UserGroup(NoDeleteModelMixin):
    '''用户组模块'''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,verbose_name=_('ID'))
    name = models.CharField(max_length=128, verbose_name=_('名称'))
    comment = models.TextField(blank=True, verbose_name=_('备注'))
    date_created = models.DateTimeField(auto_now_add=True, null=True,
                                        verbose_name=_('创建日期'))
    created_by = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name
    __str__ = __unicode__

    def delete(self, using=None, keep_parents=False):
        if self.name != '监控系统':
            self.users.clear()
            return super(UserGroup, self).delete()
        return True

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('users:user-group-detail', args=(self.pk,))

    @classmethod
    def initial(cls):
        default_group = cls.objects.filter(name='监控系统')
        if not default_group:
            group = cls(name='监控系统', created_by='System', comment='监控系统')
            group.save()
        else:
            group = default_group[0]
        return group

    @classmethod
    def generate_fake(cls):
        from random import seed, choice
        import forgery_py
        from . import User
        groups = ["管理员", "普通用户", "主机用户", "数据库用户", "网页用户"]

        seed()
        for i in groups:
            group = cls(name=groups[groups.index(i)],
                        comment=forgery_py.lorem_ipsum.sentence(),
                        created_by=choice(User.objects.all()).username)
            try:
                group.save()
            except IntegrityError:
                print('Error continue')
                continue
