# coding: utf-8
#

from common.utils import setattr_bulk
from django.shortcuts import reverse
from django.http import HttpResponseRedirect



def get_user_granted_assets_direct(user):
    """Return assets granted of the user directly
     :param user: Instance of :class: ``User``
     :return: {asset1: {system_user1, system_user2}, asset2: {...}}
    """
    assets = {}
    asset_permissions_direct = user.asset_permissions.all()

    for asset_permission in asset_permissions_direct:
        if not asset_permission.is_valid:
            continue
        for asset in asset_permission.get_granted_assets():
            if not asset.is_active:
                continue
            if asset in assets:
                assets[asset] |= set() 
            else:
                setattr(asset, 'inherited', False)
                assets[asset] = set() 
    return assets

def get_user_granted_assets(user):
    """Return assets granted of the user inherit from user groups

    :param user: Instance of :class: ``User``
    :return: {asset1: {system_user1, system_user2}, asset2: {...}}
    """
    assets_direct = get_user_granted_assets_direct(user)
    assets_inherited = {}
    assets = assets_inherited

    for asset in assets_direct:
        if not asset.is_active:
            continue
        if asset in assets:
            assets[asset] |= assets_direct[asset]
        else:
            assets[asset] = assets_direct[asset]
    return assets

def get_user_group_asset_permissions(user_group):
    permissions = user_group.asset_permissions.all()
    return permissions

def get_user_asset_permissions(user):
    user_group_permissions = set()
    direct_permissions = set(setattr_bulk(user.asset_permissions.all(), 'inherited', 0))

    for user_group in user.groups.all():
        permissions = get_user_group_asset_permissions(user_group)
        user_group_permissions |= set(permissions)
    user_group_permissions = set(setattr_bulk(user_group_permissions, 'inherited', 1))
    return direct_permissions | user_group_permissions

def require_role(role='user'):
    """
    decorator for require user role in ["super", "admin", "user"]
    要求用户是某种角色 ["super", "admin", "user"]的装饰器
    """

    def _deco(func):
        def __deco(request, *args, **kwargs):
            request.session['pre_url'] = request.path
            if not request.user.is_authenticated():
                return HttpResponseRedirect(reverse('users:login'))
            if role == 'admin':
                if not request.user.is_superuser:
                    return HttpResponseRedirect(reverse('users:forbidden'))
            return func(request, *args, **kwargs)
        return __deco
    return _deco