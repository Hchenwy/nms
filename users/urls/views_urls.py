# coding: utf-8
'''URL 指定'''
from __future__ import absolute_import
from django.conf.urls import url
from .. import views

app_name = 'users'

urlpatterns = [
    # Login view
    url(r'^login$', views.UserLoginView.as_view(), name='login'),
    url(r'^logout$', views.UserLogoutView.as_view(), name='logout'),
    url(r'^user-forbidden$', views.UserForbiddenView.as_view(), name='forbidden'),
    url(r'^password/reset$', views.UserResetPasswordView.as_view(), name='reset-password'),
    url(r'^password/forgot$', views.UserForgotPasswordView.as_view(), name='forgot-password'),
    url(r'^password/reset/success$', views.UserResetPasswordSuccessView.as_view(), name='reset-password-success'),

    # User view
    url(r'^user$', views.UserListView.as_view(), name='user-list'),
    url(r'^user/create$', views.UserCreateView.as_view(), name='user-create'),
    url(r'^user-list-json$', views.UserUserListJson.as_view(), name='user-list-json'),
    url(r'^user/(?P<pk>[^/]+)$', views.UserDetailView.as_view(), name='user-detail'),
    url(r'^first-login/$', views.UserFirstLoginView.as_view(), name='user-first-login'),
    url(r'^user/(?P<pk>[^/]+)/update$', views.UserUpdateView.as_view(), name='user-update'),

    # User group view
    url(r'^user-group/create$', views.UserGroupCreateView.as_view(), name='user-group-create'),
    url(r'^user-group$', views.UserGroupListView.as_view(), name='user-group-list'),
    url(r'^user-group-list$', views.UserGroupListJson.as_view(), name='user-group-list-json'),
    url(r'^user-group/(?P<pk>[^/]+)$', views.UserGroupDetailView.as_view(), name='user-group-detail'),
    url(r'^user-group/(?P<pk>[^/]+)/update$', views.UserGroupUpdateView.as_view(), name='user-group-update'),
]