# coding:utf-8
from django import forms
#from django.utils.translation import ugettext as _
#from zalt.passwd_api import passwordstrength
from .models.zabbix import Zabbix


class NodeForm(forms.ModelForm):
    class Meta:
        model = Zabbix
        fields = ['name', "bandwidth", "operator", 'contacts', 'phone', 'address', 'comment', 'zbx_url', 'zbx_ip', 'zbx_user', 'zbx_passwd', 'zbx_mysql_user', 'zbx_mysql_passwd', 'zbx_mysql_port']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Node Name', 'class': 'form-control'}),
            'address': forms.TextInput(attrs={'placeholder': 'Address', 'class': 'form-control'}),
            'bandwidth': forms.TextInput(attrs={'placeholder': 'Bandwidth', 'class': 'form-control'}),
            'operator': forms.TextInput(attrs={'placeholder': 'Operator', 'class': 'form-control'}),
            'contacts': forms.TextInput(attrs={'placeholder': 'Contacts', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone', 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
            'zbx_user': forms.TextInput(attrs={'placeholder': 'Zabbix User', 'class': 'form-control'}),
            'zbx_passwd': forms.PasswordInput(attrs={'placeholder': 'Zabbix Password', 'class': 'form-control'}),
            'zbx_url': forms.TextInput(attrs={'placeholder': 'Zabbix Api Url', 'class': 'form-control'}),
            'zbx_ip': forms.TextInput(attrs={'placeholder': 'Zabbix IP Address', 'class': 'form-control'}),
            'zbx_mysql_user': forms.TextInput(attrs={'placeholder': 'Mysql User', 'class': 'form-control'}),
            'zbx_mysql_passwd': forms.PasswordInput(attrs={'placeholder': 'Mysql Password', 'class': 'form-control'}),
            'zbx_mysql_port': forms.TextInput(attrs={'placeholder': 'Mysql Port', 'class': 'form-control'}),
        }

    def clean(self):
        #zbx_passwd_score = passwordstrength(self.cleaned_data['zbx_passwd'].encode("utf-8")).score
        #zbx_mysql_passwd_score = passwordstrength(self.cleaned_data['zbx_mysql_passwd'].encode("utf-8")).score
        if self.cleaned_data['zbx_passwd']:
            #if zbx_passwd_score > 70:
            pass
                #self.cleaned_data['zbx_passwd'] =  bcrypt.hashpw(self.cleaned_data['zbx_passwd'].encode("utf-8"), bcrypt.gensalt())
            #else:
                #raise forms.ValidationError(_(u'Zabbix  密码评分：' + str(zbx_passwd_score) + '. Too simple!!'), code='511')
        else:
            self.cleaned_data.pop('zbx_passwd')
        if self.cleaned_data['zbx_mysql_passwd']:
            #if zbx_mysql_passwd_score > 70:
            pass
                #self.cleaned_data['salt_passwd'] =  bcrypt.hashpw(self.cleaned_data['salt_passwd'].encode("utf-8"), bcrypt.gensalt())
            #else:
                #raise forms.ValidationError(_(u'Salt 密码评分：' + str(salt_passwd_score) + '. Too simple!!'), code='511')
        else:
            self.cleaned_data.pop('zbx_mysql_passwd')
        return self.cleaned_data
