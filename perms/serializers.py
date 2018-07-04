# -*- coding: utf-8 -*-
#

from rest_framework import serializers
from .models import AssetPermission


class AssetPermissionSerializer(serializers.ModelSerializer):
    assets_ = serializers.SerializerMethodField()
    asset_groups_ = serializers.SerializerMethodField()
    users_ = serializers.SerializerMethodField()
    user_groups_ = serializers.SerializerMethodField()

    class Meta:
        model = AssetPermission
        fields = '__all__'

    @staticmethod
    def get_assets_(obj):
        return [asset.hostname for asset in obj.assets.all()]

    @staticmethod
    def get_asset_groups_(obj):
        return [group.name for group in obj.asset_groups.all()]

    @staticmethod
    def get_users_(obj):
        return [user.username for user in obj.users.all()]

    @staticmethod
    def get_user_groups_(obj):
        return [group.name for group in obj.user_groups.all()]

class UserAssetPermissionSerializer(AssetPermissionSerializer):
    is_inherited = serializers.SerializerMethodField()

    @staticmethod
    def get_is_inherited(obj):
        if getattr(obj, 'inherited', ''):
            return True
        else:
            return False