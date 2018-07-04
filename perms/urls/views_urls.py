# coding:utf-8

from django.conf.urls import url
from .. import views

app_name = 'perms'

urlpatterns = [
    url(r'^asset-permission$', views.AssetPermissionListView.as_view(), name='asset-permission-list'),
    url(r'^asset-permission/create$', views.AssetPermissionCreateView.as_view(), name='asset-permission-create'),
    url(r'^asset-permission-list-json$', views.AssetPermissionListJson.as_view(), name='asset-permission-list-json'),
    url(r'^asset-permission/(?P<pk>[^/]+)$', views.AssetPermissionDetailView.as_view(),name='asset-permission-detail'),
]

