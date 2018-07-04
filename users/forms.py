# ~*~ coding: utf-8 ~*~

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from captcha.fields import CaptchaField

from .models import User, UserGroup

class UserLoginForm(AuthenticationForm):
    '''用户登录表单'''
    username = forms.CharField(label=_('Username'), max_length=100)
    password = forms.CharField(
        label=_('Password'), widget=forms.PasswordInput, max_length=100,
        strip=False)
    captcha = CaptchaField()

class UserProfileForm(forms.ModelForm):
    '''用户信息表单'''
    class Meta:
        model = User
        fields = [
            'username', 'name', 'email',
            'wechat', 'phone', 'dingtalk',
        ]
        help_texts = {
            'username': '* 必填',
            'name': '* 必填',
            'email': '* 必填',
        }

class UserGroupForm(forms.ModelForm):
    class Meta:
        model = UserGroup
        fields = [
            'name', 'comment'
        ]
        help_texts = {
            'name': '* 必填'
        }

class UserCreateUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username', 'name', 'email', 'groups', 'wechat', 'dingtalk',
            'phone', 'department', 'position', 'role', 'date_expired', 'comment',
        ]
        help_texts = {
            'username': '* 必填',
            'name': '* 必填',
            'email': '* 必填',
        }
        widgets = {
            'groups': forms.SelectMultiple(
                attrs={'class': 'chosen-select',
                       'data-placeholder': _('加入用户组')}),
        }
