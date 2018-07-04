# -*- coding: utf-8 -*-
#

from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _


class LoginLog(models.Model):
    ''' 用户登录日志模块 '''
    LOGIN_TYPE_CHOICE = (
        ('W', 'Web'),
        ('ST', 'SSH Terminal')
    )

    username = models.CharField(max_length=20, verbose_name=_('Username'))
    name = models.CharField(max_length=20, blank=True, verbose_name=_('Name'))
    login_type = models.CharField(choices=LOGIN_TYPE_CHOICE, max_length=2,
                                  verbose_name=_('Login type'))
    login_ip = models.GenericIPAddressField(verbose_name=_('Login ip'))
    login_city = models.CharField(max_length=254, blank=True, null=True,
                                  verbose_name=_('Login city'))
    user_agent = models.CharField(max_length=254, blank=True, null=True,
                                  verbose_name=_('User agent'))
    date_login = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_('Date login'))

    class Meta:
        db_table = 'login_log'
        ordering = ['-date_login', 'username']
