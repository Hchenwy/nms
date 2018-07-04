#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^alert_list/$', alert_list, name='alert_list'),
    url(r'^alert_list_json/$', alert_list_json, name='alert_list_json'),
    url(r'^alert_edit/$', alert_edit, name='alert_edit'),
    url(r'^alert_save/$', alert_save, name='alert_save'),
]