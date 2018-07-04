# coding:utf-8

from django.conf.urls import url
from rest_framework import routers
from .. import api

app_name = 'perms'

router = routers.DefaultRouter()
router.register('v1/asset-permissions',
                api.AssetPermissionViewSet,
                'asset-permission')
urlpatterns = [

]

urlpatterns += router.urls