
from common.mixins import IDInFilterMixin
from rest_framework_bulk import BulkModelViewSet
from rest_framework.response import Response
from rest_framework import viewsets, status


from .models import AssetGroup, Asset, IDC
from .hands import IsSuperUser, IsValidUser,  get_user_granted_assets
from . import serializers



class AssetViewSet(IDInFilterMixin, BulkModelViewSet):
    """API endpoint that allows Asset to be viewed or edited."""
    queryset = Asset.objects.all()
    serializer_class = serializers.AssetSerializer
    permission_classes = (IsSuperUser,)

    def get_queryset(self):
        IDC_id = self.request.query_params.get('IDC_id', '')
        asset_group_id = self.request.query_params.get('asset_group_id', '')
        if IDC_id:
            queryset = queryset.filter(IDC__id=IDC_id)
        if asset_group_id:
            queryset = queryset.filter(groups__id=asset_group_id)
        return queryset

class AssetGroupViewSet(IDInFilterMixin, BulkModelViewSet):
    queryset = AssetGroup.objects.all()
    serializer_class = serializers.AssetGroupSerializer
    permission_classes = (IsSuperUser,)


class IDCViewSet(IDInFilterMixin, BulkModelViewSet):
    """
    IDC api set, for add,delete,update,list,retrieve resource
    """
    queryset = IDC.objects.all()
    serializer_class = serializers.IDCSerializer
    permission_classes = (IsSuperUser,)