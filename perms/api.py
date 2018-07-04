# ~*~ coding: utf-8 ~*~
# 
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from users.permissions import IsSuperUser
from .models import AssetPermission
from .utils import get_user_granted_assets, get_user_asset_permissions, get_user_group_asset_permissions
from .hands import User, UserGroup
from . import serializers





class AssetPermissionViewSet(viewsets.ModelViewSet):
    """
    资产授权列表的增删改查api
    """
    queryset = AssetPermission.objects.all()
    serializer_class = serializers.AssetPermissionSerializer
    permission_classes = (IsSuperUser,)

    def get_queryset(self):
        queryset = super(AssetPermissionViewSet, self).get_queryset()
        user_id = self.request.query_params.get('user', '')
        user_group_id = self.request.query_params.get('user_group', '')

        if user_id and user_id.isdigit():
            user = get_object_or_404(User, id=int(user_id))
            queryset = get_user_asset_permissions(user)

        if user_group_id:
            user_group = get_object_or_404(UserGroup, id=user_group_id)
            queryset = get_user_group_asset_permissions(user_group)
        return queryset

    def get_serializer_class(self):
        if getattr(self, 'user_id', ''):
            return serializers.UserAssetPermissionSerializer
        return serializers.AssetPermissionSerializer
