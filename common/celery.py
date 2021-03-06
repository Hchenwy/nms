# ~*~ coding: utf-8 ~*~

from __future__ import absolute_import, unicode_literals
import os
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nms.settings')

from django.conf import settings

app = Celery('nms')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: [app_config.split('.')[0]
                                for app_config in settings.INSTALLED_APPS])