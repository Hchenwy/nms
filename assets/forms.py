# coding:utf-8
from django import forms
from .models import Asset, AssetGroup, IDC
from django.utils.translation import gettext_lazy as _


class AssetCreateForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'ip', 'hostname', 'groups', 'IDC', 'is_active', 'type', 'env',
            'status', 'public_ip', 'remote_card_ip', 'cabinet_no', 'cabinet_pos',
            'number', 'vendor', 'model', 'sn', 'cpu_model', 'cpu_count', 'cpu_cores',
            'memory', 'disk_total', 'disk_info', 'platform', 'os', 'os_version',
            'os_arch', 'comment',
        ]
        widgets = {
            'groups': forms.SelectMultiple(
                attrs={'class': 'chosen-select',
                       'data-placeholder': _('选择设备组')}),
        }
        help_texts = {
            'hostname': '* 必填',
            'ip': '* 必填',
        }

class AssetGroupForm(forms.ModelForm):
    
    assets = forms.ModelMultipleChoiceField(
        queryset=Asset.objects.all(),
        label=_('Asset'),
        required=False,
        widget=forms.SelectMultiple(
            attrs={'class': 'chosen-select', 'data-placeholder': _('选择设备')})
        )

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance', None):
            initial = kwargs.get('initial', {})
            initial['assets'] = kwargs['instance'].assets.all()
        super(AssetGroupForm, self).__init__(*args, **kwargs)
    
    def _save_m2m(self):
        super(AssetGroupForm, self)._save_m2m()
        assets = self.cleaned_data['assets']
        self.instance.assets.clear()
        self.instance.assets.add(*tuple(assets))

    class Meta:
        model = AssetGroup
        fields = [
            "name", "comment",
        ]
        help_texts = {
            'name': '* 必填',
        }


class AssetUpdateForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'hostname', 'ip', 'groups', 'IDC', 'is_active',
            'type', 'env', 'status', 'public_ip', 'remote_card_ip', 'cabinet_no',
            'cabinet_pos', 'number', 'comment'
        ]
        widgets = {
            'groups': forms.SelectMultiple(
                attrs={'class': 'chosen-select',
                       'data-placeholder': _('选择资产组')}),
        }
        help_texts = {
            'hostname': '* 必填',
            'ip': '* 必填',
        }

class IDCForm(forms.ModelForm):
    class Meta:
        model = IDC
        fields = ['name', "bandwidth", "operator", 'contact', 
                  'phone', 'address', 'intranet', 'extranet', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('名称')}),
            'intranet': forms.Textarea(attrs={'placeholder': 'IP段之间用逗号隔开，如：192.168.1.0/24,192.168.1.0/24'}),
            'extranet': forms.Textarea(attrs={'placeholder': 'IP段之间用逗号隔开，如：201.1.32.1/24,202.2.32.1/24'})
        }
        help_texts = {
            'name': '* 必填',
        }

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance', None):
            initial = kwargs.get('initial', {})
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=commit)
        return instance


class FileForm(forms.Form):
    file = forms.FileField()