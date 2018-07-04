from django import forms
from users.models import User
from django.utils.translation import ugettext_lazy as _

from .models import AssetPermission

class AssetPermissionForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(
            attrs={'class': 'chosen-select', 'data-placeholder': _('选择用户')},
        ),
        label=_("用户"),
        required=False,
    )

    class Meta:
        model = AssetPermission
        fields = [
            'name', 'users', 'user_groups', 'assets', 'asset_groups',
            'is_active', 'date_expired', 'comment',
        ]
        widgets = {
            'user_groups': forms.SelectMultiple(
                attrs={'class': 'chosen-select',
                       'data-placeholder': _('选择用户组')}),
            'assets': forms.SelectMultiple(
                attrs={'class': 'chosen-select',
                       'data-placeholder': _('选择资产')}),
            'asset_groups': forms.SelectMultiple(
                attrs={'class': 'chosen-select',
                       'data-placeholder': _('选择资产组')}),
        }
        help_texts = {
            'name': '* 必填',
        }