# coding:utf-8
from __future__ import absolute_import, unicode_literals
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.urls import reverse_lazy
from django.utils.timezone import localtime

from ..hands import AdminUserRequiredMixin, UserRequiredMixin
from ..models import IDC, Asset
from .. import forms



__all__ = ['IDCListView', 'IDCListJson', 'IDCDetailView', 'IDCCreateView', 'IDCUpdateView']


class IDCListView(UserRequiredMixin, TemplateView):
    template_name = 'assets/asset_IDC_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('资产'),
            'action': _('机房列表'),
            # 'keyword': self.request.GET.get('keyword', '')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class IDCListJson(UserRequiredMixin, BaseDatatableView):
    model = IDC
    columns = ["id", "name", "asset_count", "bandwidth", "id", "address",
               "contact", "phone", "intranet", "extranet", "operator",
               "created_by", "date_created", "comment"]
    order_columns = ["id", "name", "bandwidth", "id", "address",
                     "contact", "phone", "intranet", "extranet", "operator", 
                     "created_by", "date_created", "comment"]
    page_length = 10

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'name':
            return super(IDCListJson, self).render_column(row, column)
        elif column == 'asset_count':
            return Asset.objects.filter(IDC=row).count()
        elif column == 'date_created':
            return str(localtime(row.date_created).replace(tzinfo=None))
        else :
            #return row.__getattribute__(column)
            return getattr(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'sSearch', None)
        if search:
           qs = qs.filter(Q(name__icontains=search) |
                          Q(bandwidth__icontains=search) |
                          Q(address__icontains=search) |
                          Q(contact__icontains=search) |
                          Q(phone__icontains=search) |
                          Q(intranet__icontains=search) |
                          Q(extranet__icontains=search) |
                          Q(operator__icontains=search))
        return qs

class IDCDetailView(AdminUserRequiredMixin, DetailView):
    model = IDC
    template_name = 'assets/IDC_detail.html'
    context_object_name = 'IDC'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('资产'),
            'action': _('机房详情'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class IDCCreateView(AdminUserRequiredMixin, CreateView):
    model = IDC
    form_class = forms.IDCForm
    template_name = 'assets/IDC_create_update.html'
    success_url = reverse_lazy('assets:IDC-list')

    def get_context_data(self, **kwargs):
        context = {
            'app': _('资产'),
            'action': _('创建机房'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        IDC = form.save(commit=False)
        IDC.created_by = self.request.user.username or 'System'
        IDC.save()
        return super().form_valid(form)

class IDCUpdateView(AdminUserRequiredMixin, UpdateView):
    model = IDC
    form_class = forms.IDCForm
    template_name = 'assets/IDC_create_update.html'
    context_object_name = 'IDC'
    success_url = reverse_lazy('assets:IDC-list')

    def form_valid(self, form):
        IDC = form.save(commit=False)
        IDC.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = {
            'app': _('资产'),
            'action': _('更新资产'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


