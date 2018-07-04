# coding:utf-8
from django.conf.urls import url
from .. import api
from rest_framework import routers
from rest_framework_bulk.routes import BulkRouter

app_name = 'assets'

router = BulkRouter()
router.register(r'v1/asset-groups', api.AssetGroupViewSet, 'asset-group')
router.register(r'v1/assets', api.AssetViewSet, 'asset')
router.register(r'v1/IDCs', api.IDCViewSet, 'IDC')


urlpatterns = [
]

urlpatterns += router.urls

