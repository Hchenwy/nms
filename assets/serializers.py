# -*- coding: utf-8 -*-
from django.core.cache import cache
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from rest_framework_bulk import BulkListSerializer, BulkSerializerMixin
from .models import AssetGroup, Asset, IDC



class AssetGroupSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    assets_amount = serializers.SerializerMethodField()
    assets = serializers.PrimaryKeyRelatedField(many=True, queryset=Asset.objects.all())

    class Meta:
        model = AssetGroup
        list_serializer_class = BulkListSerializer
        fields = ['id', 'name', 'comment', 'assets_amount', 'assets']

    @staticmethod
    def get_assets_amount(obj):
        return obj.assets.count()

class AssetSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    # system_users = SystemUserSerializer(many=True, read_only=True)
    # admin_user = AdminUserSerializer(many=False, read_only=True)
    hardware = serializers.SerializerMethodField()
    is_online = serializers.SerializerMethodField()

    class Meta(object):
        model = Asset
        list_serializer_class = BulkListSerializer
        fields = '__all__'

    @staticmethod
    def get_hardware(obj):
        if obj.cpu_count:
            return '{} Core {} {}'.format(obj.cpu_count*obj.cpu_cores, obj.memory, obj.disk_total)
        else:
            return ''

    @staticmethod
    def get_is_online(obj):
        hostname = obj.hostname
        if cache.get(hostname) == '1':
            return True
        elif cache.get(hostname) == '0':
            return False
        else:
            return 'Unknown'

    def get_field_names(self, declared_fields, info):
        fields = super(AssetSerializer, self).get_field_names(declared_fields, info)
        fields.extend(['get_type_display', 'get_env_display'])
        return fields

class IDCSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    """
    IDC
    """
    assets_amount = serializers.SerializerMethodField()
    assets = serializers.PrimaryKeyRelatedField(many=True, queryset=Asset.objects.all())

    class Meta:
        model = IDC
        fields = '__all__'

    @staticmethod
    def get_assets_amount(obj):
        return obj.assets.count()