from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.timezone import localtime
from django.shortcuts import render
from django.views.generic import CreateView, DetailView
from django.views.generic.base import TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from .models import AssetPermission
from .forms import AssetPermissionForm
from .hands import AdminUserRequiredMixin



# Create your views here.

class AssetPermissionCreateView(AdminUserRequiredMixin, SuccessMessageMixin, CreateView):
    model = AssetPermission
    form_class = AssetPermissionForm
    template_name = 'perms/asset_permission_create_update.html'
    success_url = reverse_lazy('perms:asset-permission-list')
    warning = None

    def get_context_data(self, **kwargs):
        context = {
            'app': _('权限管理'),
            'action': _('创建资产权限'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        assetpermission = form.save(commit=False)
        assetpermission.created_by = self.request.user.username or 'System'
        assetpermission.save()
        return super().form_valid(form)
    

    def get_success_message(self, cleaned_data):
        url = reverse_lazy(
            'perms:asset-permission-detail',
            kwargs={'pk': self.object.pk}
        )
        success_message = _(
            'Create asset permission <a href="{url}"> {name} </a> '
            'success.'.format(url=url, name=self.object.name)
        )
        return success_message

class AssetPermissionListView(AdminUserRequiredMixin, TemplateView):
    model = AssetPermission
    context_object_name = 'asset_permission_list'
    template_name = 'perms/asset_permission_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('权限管理'),
            'action': _('资产权限列表'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class AssetPermissionListJson(AdminUserRequiredMixin, BaseDatatableView):
    model = AssetPermission
    columns = ["id", "name", "users", "user_groups", "assets", 
               "asset_groups", "is_active", "id", "date_expired", "created_by", 
               "date_created", "comment", ]
    order_columns = ["id", "name", "users", "user_groups", "assets", 
                     "asset_groups", "is_active", "id", "date_expired", "created_by", 
                     "date_created", "comment", ]
    page_length = 10

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'date_created':
            return str(localtime(row.date_created).replace(tzinfo=None))
        elif column == 'name':
            return super(AssetPermissionListJson, self).render_column(row, column)
        elif column == 'date_expired':
            return str(localtime(row.date_expired).replace(tzinfo=None))
        elif column == 'is_active' :
            if getattr(row, column):
                return "enable"
            else:
                return "disable"
        elif column in ["users", "user_groups", "assets", "asset_groups"]:
            #return str(localtime(row.date_expired).replace(tzinfo=None))
            names = []
            obj = getattr(row, column)
            for qureryset in obj.all():
                if column == "assets":
                    names.append(qureryset.hostname)
                else:
                    names.append(qureryset.name)
            return ",".join(names) 
        else:
            #return row.__getattribute__(column)
            return getattr(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'sSearch', None)
        if search:
           qs = qs.filter(Q(name__icontains=search))
        return qs

class AssetPermissionDetailView(AdminUserRequiredMixin, DetailView):
    template_name = 'perms/asset_permission_detail.html'
    context_object_name = 'asset_permission'
    model = AssetPermission

    def get_context_data(self, **kwargs):
        context = {
            'app': _('权限管理'),
            'action': _('资产权限详情'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)