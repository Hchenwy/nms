from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, reverse
from assets.models import Asset, AssetGroup, IDC
from users.models import  User, UserGroup

from common.mixins import JSONResponseMixin
from .echarts import Heatmap, Barmap, Treemap, get_sumary_js

#REMOTE_HOST = "https://pyecharts.github.io/assets/js"

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    hmap = Heatmap()
    barmap = Barmap()
    #treemap = Treemap()

    def get(self, request, *args, **kwargs):
        #if not request.user.is_superuser:
        #    return redirect('assets:user-asset-list')
        return super(IndexView, self).get(request, *args, **kwargs)
    
    @staticmethod
    def get_user_count():
        return User.objects.filter(role__in=('Admin', 'User')).count()

    @staticmethod
    def get_user_group_count():
        return UserGroup.objects.all().count()

    @staticmethod
    def get_asset_count():
        return Asset.objects.all().count()

    @staticmethod
    def get_asset_group_count():
        return AssetGroup.objects.all().count()

    @staticmethod
    def get_IDC_count():
        return IDC.objects.all().count()

    def get_context_data(self, **kwargs):
        context = {
            #'host':REMOTE_HOST,
            #'script_list':self.treemap.get_js_dependencies(),
            'e_hmap': self.hmap.render_embed(),
            'e_barmap': self.barmap.render_embed(),
            #'e_treemap': self.treemap.render_embed(),
            'users_count': self.get_user_count(),
            'users_group_count': self.get_user_group_count(),
            'assets_count': self.get_asset_count(),
            'assets_group_count': self.get_asset_group_count(),
            'IDC_count': self.get_IDC_count(),
        }

        kwargs.update(context)
        return super(IndexView, self).get_context_data(**kwargs)


#class SumaryJson(LoginRequiredMixin, JSONResponseMixin, TemplateView):
#    def render_to_response(self, context, **response_kwargs)
#        data = get_sumary_js()
#        return self.render_json_response(data)