import uuid
from django.db import models

# Create your models here.

from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.shortcuts import reverse

from common.utils import date_expired_default


class AssetPermission(models.Model):
    from users.models import User, UserGroup
    from assets.models import Asset, AssetGroup, IDC
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=128, unique=True, verbose_name=_('名称'))
    users = models.ManyToManyField(User, related_name='asset_permissions', blank=True, verbose_name=_("用户"))
    user_groups = models.ManyToManyField(UserGroup, related_name='asset_permissions', blank=True, verbose_name=_("用户组"))
    assets = models.ManyToManyField(Asset, related_name='granted_by_permissions', blank=True, verbose_name=_("资产"))
    asset_groups = models.ManyToManyField(AssetGroup, related_name='granted_by_permissions', blank=True, verbose_name=_("资产组"))
    is_active = models.BooleanField(default=True, verbose_name=_('激活'))
    date_expired = models.DateTimeField(default=date_expired_default, verbose_name=_('过期日期'))
    created_by = models.CharField(max_length=128, blank=True, verbose_name=_('创建者'))
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_('创建日期'))
    comment = models.TextField(verbose_name=_('备注'), blank=True)

    def __str__(self):
        return self.name

    @property
    def is_valid(self):
        if self.date_expired > timezone.now() and self.is_active:
            return True
        return False

    def get_absolute_url(self):
        return reverse('perms:asset-permission-detail', args=(self.pk,))

    def get_granted_users(self):
        return list(set(self.users.all()) | self.get_granted_user_groups_member())

    def get_granted_user_groups_member(self):
        users = set()
        for user_group in self.user_groups.all():
            for user in user_group.users.all():
                setattr(user, 'is_inherit_from_user_groups', True)
                setattr(user, 'inherit_from_user_groups',
                        getattr(user, 'inherit_from_user_groups', set()).add(user_group))
                users.add(user)
        return users

    def get_granted_assets(self):
        return list(set(self.assets.all()) | self.get_granted_asset_groups_member())

    def get_granted_asset_groups_member(self):
        assets = set()
        for asset_group in self.asset_groups.all():
            for asset in asset_group.assets.all():
                setattr(asset, 'is_inherit_from_asset_groups', True)
                setattr(asset, 'inherit_from_asset_groups',
                        getattr(asset, 'inherit_from_user_groups', set()).add(asset_group))
                assets.add(asset)
        return assets
