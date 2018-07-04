#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
#
from __future__ import absolute_import

from django.conf.urls import url
from rest_framework_bulk.routes import BulkRouter
from .. import api

app_name = 'users'

router = BulkRouter()
router.register(r'v1/users', api.UserViewSet, 'user')
router.register(r'v1/user-groups', api.UserGroupViewSet, 'user-group')
urlpatterns = [
    url(r'^v1/users/(?P<pk>[^/]+)/password/reset/$', api.UserResetPasswordApi.as_view(), name='user-reset-password'),
]


urlpatterns += router.urls
