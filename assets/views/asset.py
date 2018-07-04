# coding:utf-8

import uuid
import json
import csv
import codecs
from io import StringIO

from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext_lazy as _
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.generic import CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.core.cache import cache
from django.utils.timezone import localtime

from common.mixins import JSONResponseMixin
from common.utils import get_object_or_none
from ..models import AssetGroup, Asset, IDC
from ..hands import AdminUserRequiredMixin, UserRequiredMixin, get_user_granted_assets
from .. import forms


class AssetListView(UserRequiredMixin, TemplateView):
    template_name = 'assets/asset_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': '资产管理',
            'action': '资产列表',
            'groups': AssetGroup.objects.all(),
            #'system_users': SystemUser.objects.all(),
            # 'form': forms.AssetBulkUpdateForm(),
        }
        kwargs.update(context)
        return super(AssetListView, self).get_context_data(**kwargs)


class AssetListJson(UserRequiredMixin, BaseDatatableView):
    model = Asset
    columns = ["id", "ip", "hostname", "os", "IDC", "id", "groups", "type", "env", "status", "public_ip",
               "remote_card_ip", "cabinet_no", "cabinet_pos", "number", "vendor", "model", 
               "sn", "cpu_model", "cpu_count", "cpu_cores", "memory", "disk_total", 
               "disk_info", "platform", "os_version", "os_arch", "created_by", 
               "date_created", "comment"]
    order_columns = ["id", "ip", "hostname", "os", "IDC", "id", "groups", "type", "env", "status", "public_ip",
               "remote_card_ip", "cabinet_no", "cabinet_pos", "number", "vendor", "model", 
               "sn", "cpu_model", "cpu_count", "cpu_cores", "memory", "disk_total", 
               "disk_info", "platform", "os_version", "os_arch", "created_by", 
               "date_created", "comment"]
    page_length = 10

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        if self.request.user.is_superuser:
            return self.model.objects.all()
        else:
            assets_granted = get_user_granted_assets(self.request.user)
            return self.model.objects.filter(id__in=[asset.id for asset in assets_granted])

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'ip':
            return super(AssetListJson, self).render_column(row, column)
        elif column == 'date_created':
            return str(localtime(row.date_created).replace(tzinfo=None))
        elif column == 'IDC':
            try : 
                return row.IDC.name
            except Exception as e:
                print("no group found, error: %s" %(e))
                return ""
        elif column == 'groups':
            g_name = "" 
            try : 
                for g_query in row.groups.all():
                    g_name = g_name + " " + g_query.name 
                return g_name
            except Exception as e:
                print("group found, error: %s" %(e))
                return g_name
        else :
            return row.__getattribute__(column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'sSearch', None)
        if search:
           qs = qs.filter(Q(ip__icontains=search) |
                          Q(hostname__icontains=search) |
                          Q(env__icontains=search) |
                          Q(public_ip__icontains=search) |
                          Q(remote_card_ip__icontains=search) |
                          Q(cabinet_no__icontains=search) |
                          Q(cabinet_pos__icontains=search) |
                          Q(number__icontains=search) |
                          Q(vendor__icontains=search) |
                          Q(model__icontains=search) |
                          Q(sn__icontains=search) |
                          Q(cpu_model__icontains=search) |
                          Q(cpu_count__icontains=search) |
                          Q(cpu_cores__icontains=search) |
                          Q(memory__icontains=search) |
                          Q(disk_total__icontains=search) |
                          Q(disk_info__icontains=search) |
                          Q(platform__icontains=search) |
                          Q(os__icontains=search) |
                          Q(os_version__icontains=search) |
                          Q(os_arch__icontains=search) |
                          Q(comment__icontains=search))
        return qs

class AssetCreateView(AdminUserRequiredMixin, CreateView):
    model = Asset
    form_class = forms.AssetCreateForm
    template_name = 'assets/asset_create.html'
    success_url = reverse_lazy('assets:asset-list')

    def form_valid(self, form):
        self.asset = asset = form.save()
        asset.created_by = self.request.user.username or 'Admin'
        asset.date_created = timezone.now()
        asset.save()
        return super(AssetCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = {
            'app': '资产管理',
            'action': '创建设备',
        }
        kwargs.update(context)
        return super(AssetCreateView, self).get_context_data(**kwargs)

    def get_success_url(self):
        #update_assets_hardware_info.delay([self.asset._to_secret_json()])
        return super(AssetCreateView, self).get_success_url()

class AssetDetailView(AdminUserRequiredMixin, DetailView):
    model = Asset
    context_object_name = 'asset'
    template_name = 'assets/asset_detail.html'

    def get_context_data(self, **kwargs):
        asset_groups = self.object.groups.all()
        context = {
            'app': '资产管理',
            'action': '资产详情',
            'asset_groups_remain': [asset_group for asset_group in AssetGroup.objects.all()
                                    if asset_group not in asset_groups],
            'asset_groups': asset_groups,
        }
        kwargs.update(context)
        return super(AssetDetailView, self).get_context_data(**kwargs)

class AssetUpdateView(AdminUserRequiredMixin, UpdateView):
    model = Asset
    form_class = forms.AssetUpdateForm
    template_name = 'assets/asset_update.html'
    success_url = reverse_lazy('assets:asset-list')

    def get_context_data(self, **kwargs):
        context = {
            'app': '资产管理',
            'action': '修改资产',
        }
        kwargs.update(context)
        return super(AssetUpdateView, self).get_context_data(**kwargs)

    def form_invalid(self, form):
        print(form.errors)
        return super(AssetUpdateView, self).form_invalid(form)


@method_decorator(csrf_exempt, name='dispatch')
class AssetExportView(View):
    def get(self, request, *args, **kwargs):
        spm = request.GET.get('spm', '')
        fields = [
            field for field in Asset._meta.fields
            if field.name not in [
                'date_created'
            ]
        ]
        filename = 'assets-{}.csv'.format(
            timezone.localtime(timezone.now()).strftime('%Y-%m-%d_%H-%M-%S'))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        response.write(codecs.BOM_UTF8)
        if self.request.user.is_superuser:
            assets = Asset.objects.all()
        else:
            assets_granted = get_user_granted_assets(self.request.user)
            assets = Asset.objects.filter(id__in=[asset.id for asset in assets_granted])
        writer = csv.writer(response, dialect='excel',
                            quoting=csv.QUOTE_MINIMAL)

        header = [field.verbose_name for field in fields]
        header.append(_('资产组'))
        writer.writerow(header)

        for asset in assets:
            groups = ','.join([group.name for group in asset.groups.all()])
            data = [getattr(asset, field.name) for field in fields]
            data.append(groups)
            writer.writerow(data)
        return response

    def post(self, request, *args, **kwargs):
        try:
            assets_id = json.loads(request.body).get('assets_id', [])
        except ValueError:
            return HttpResponse('Json object not valid', status=400)
        spm = uuid.uuid4().hex
        cache.set(spm, assets_id, 300)
        url = reverse_lazy('assets:asset-export') + '?spm=%s' % spm
        return JsonResponse({'redirect': url})
    
class BulkImportAssetView(AdminUserRequiredMixin, JSONResponseMixin, FormView):
    form_class = forms.FileForm

    def form_valid(self, form):
        file = form.cleaned_data['file']
        data = file.read().decode('utf-8').strip(
            codecs.BOM_UTF8.decode('utf-8'))
        csv_file = StringIO(data)
        reader = csv.reader(csv_file)
        csv_data = [row for row in reader]
        fields = [
            field for field in Asset._meta.fields
            if field.name not in [
                'date_created'
            ]
        ]
        header_ = csv_data[0]
        mapping_reverse = {field.verbose_name: field.name for field in fields}
        mapping_reverse[_('资产组')] = 'groups'
        attr = [mapping_reverse.get(n, None) for n in header_]
        if None in attr:
            data = {'valid': False,
                    'msg': 'Must be same format as '
                           'template or export file'}
            return self.render_json_response(data)

        created, updated, failed = [], [], []
        assets = []
        for row in csv_data[1:]:
            if set(row) == {''}:
                continue
            asset_dict = dict(zip(attr, row))
            id_ = asset_dict.pop('id', 0)
            asset = get_object_or_none(Asset, id=id_)
            for k, v in asset_dict.items():
                if k == 'IDC':
                    v = get_object_or_none(IDC, name=v)
                elif k == 'is_active':
                    v = bool(v)
                elif k in ['port', 'cabinet_pos', 'cpu_count', 'cpu_cores']:
                    try:
                        v = int(v)
                    except ValueError:
                        v = 0
                elif k == 'groups':
                    groups_name = v.split(',')
                    v = AssetGroup.objects.filter(name__in=groups_name)
                else:
                    continue
                asset_dict[k] = v

            if not asset:
                try:
                    groups = asset_dict.pop('groups')
                    asset = Asset.objects.create(**asset_dict)
                    asset.groups.set(groups)
                    created.append(asset_dict['hostname'])
                    assets.append(asset)
                except IndexError as e:
                    failed.append('%s: %s' % (asset_dict['hostname'], str(e)))
            else:
                for k, v in asset_dict.items():
                    if k == 'groups':
                        asset.groups.set(v)
                        continue
                    if v:
                        setattr(asset, k, v)
                try:
                    asset.save()
                    updated.append(asset_dict['hostname'])
                except Exception as e:
                    failed.append('%s: %s' % (asset_dict['hostname'], str(e)))

        if assets:
            #update_assets_hardware_info.delay(assets)
            print(assets)

        data = {
            'created': created,
            'created_info': 'Created {}'.format(len(created)),
            'updated': updated,
            'updated_info': 'Updated {}'.format(len(updated)),
            'failed': failed,
            'failed_info': 'Failed {}'.format(len(failed)),
            'valid': True,
            'msg': 'Created: {}. Updated: {}, Error: {}'.format(
                len(created), len(updated), len(failed))
        }
        return self.render_json_response(data)