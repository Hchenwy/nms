# coding:utf-8
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import  CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from ..models import Asset, AssetGroup
from ..hands import AdminUserRequiredMixin, UserRequiredMixin
from ..forms import AssetCreateForm, AssetGroupForm




class AssetGroupListView(UserRequiredMixin, TemplateView):
    template_name = 'assets/asset_group_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('资产'),
            'action': _('资产组列表'),
            'assets': Asset.objects.all(),
            'keyword': self.request.GET.get('keyword', '')
        }
        kwargs.update(context)
        return super(AssetGroupListView, self).get_context_data(**kwargs)

class AssetGroupListJson(BaseDatatableView):
    model = AssetGroup
    columns = ["id", "name", "created_by", "comment", "id"]
    order_columns = ["id", "name", "created_by", "comment", "id"]
    page_length = 10

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'created_by':
            return row.assets.count()
        elif column == 'name':
            return super(AssetGroupListJson, self).render_column(row, column)
        else:
            #return row.__getattribute__(column)
            return getattr(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'sSearch', None)
        if search:
           qs = qs.filter(name__icontains=search)
        return qs


class AssetGroupCreateView(AdminUserRequiredMixin, CreateView):
    model = AssetGroup
    form_class = AssetGroupForm
    template_name  = 'assets/asset_group_create.html'
    success_url = reverse_lazy('assets:asset-group-list')
    
    def get_context_data(self, **kwargs):
        context = {
            'app': _('资产'),
            'action': _('创建设备组'),
            #'asset_count': 0,
        }
        kwargs.update(context)
        return super(AssetGroupCreateView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        asset_group = form.save()
        assets_id_list = self.request.POST.getlist('assets', [])
        assets = [get_object_or_404(Asset, id=int(asset_id))
                  for asset_id in assets_id_list]
        asset_group.created_by = self.request.user.username or 'Admin'
        asset_group.assets.add(*tuple(assets))
        asset_group.save()
        return super(AssetGroupCreateView, self).form_valid(form)


class AssetGroupDetailView(AdminUserRequiredMixin, DetailView):
    model = AssetGroup
    template_name = 'assets/asset_group_detail.html'
    context_object_name = 'asset_group'

    def get_context_data(self, **kwargs):
        assets_remain = Asset.objects.exclude(id__in=self.object.assets.all())
        context = {
            'app': _('资产'),
            'action': _('资产组详情'),
            'assets_remain': assets_remain,
            'assets': [asset for asset in Asset.objects.all()
                       if asset not in assets_remain],
        }
        kwargs.update(context)
        return super(AssetGroupDetailView, self).get_context_data(**kwargs)

class AssetGroupUpdateView(AdminUserRequiredMixin, UpdateView):
    model = AssetGroup
    form_class = AssetGroupForm
    template_name = 'assets/asset_group_create.html'
    success_url = reverse_lazy('assets:asset-group-list')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=AssetGroup.objects.all())
        return super(AssetGroupUpdateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        assets_all = self.object.assets.all()
        context = {
            'app': _('资产管理'),
            'action': _('编辑资产组'),
            'assets_on_list': assets_all,
            'assets_count': len(assets_all),
            'group_id': self.object.id,
        }
        kwargs.update(context)
        return super(AssetGroupUpdateView, self).get_context_data(**kwargs)