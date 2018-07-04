# coding:utf-8
from django.conf.urls import url
from .. import views

app_name = 'assets'

urlpatterns = [
    # Resource asset url
    url(r'asset/$', views.AssetListView.as_view(), name='asset-list'),
    url(r'^asset-list-json$', views.AssetListJson.as_view(), name='asset-list-json'),
    url(r'^asset/create/$', views.AssetCreateView.as_view(), name='asset-create'),
    url(r'^asset/export/$', views.AssetExportView.as_view(), name='asset-export'),
    url(r'^asset/(?P<pk>[^/]+)/$', views.AssetDetailView.as_view(), name='asset-detail'),
    url(r'^asset/(?P<pk>[^/]+)/update/$', views.AssetUpdateView.as_view(), name='asset-update'),
    url(r'^asset/import/$', views.BulkImportAssetView.as_view(), name='asset-import'),
    
    # Resource asset group url
    url(r'^asset-group/$', views.AssetGroupListView.as_view(), name='asset-group-list'),
    url(r'^asset-group-list-json$', views.AssetGroupListJson.as_view(), name='asset-group-list-json'),
    url(r'^asset-group/create/$', views.AssetGroupCreateView.as_view(), name='asset-group-create'),
    url(r'^asset-group/(?P<pk>[^/]+)/$', views.AssetGroupDetailView.as_view(), name='asset-group-detail'),
    url(r'^asset-group/(?P<pk>[^/]+)/update/$', views.AssetGroupUpdateView.as_view(), name='asset-group-update'),

    # Resource IDC url
    url(r'^IDC/$', views.IDCListView.as_view(), name='IDC-list'),
    url(r'^IDC-list-json$', views.IDCListJson.as_view(), name='IDC-list-json'),
    url(r'^IDC/create/$', views.IDCCreateView.as_view(), name='IDC-create'),
    url(r'^IDC/(?P<pk>[^/]+)/$', views.IDCDetailView.as_view(), name='IDC-detail'),
    url(r'^IDC/(?P<pk>[^/]+)/update/$', views.IDCUpdateView.as_view(), name='IDC-update'),

]

