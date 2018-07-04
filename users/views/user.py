# ~*~ coding: utf-8 ~*~
'''用户视图'''
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic.edit import (CreateView, UpdateView, FormMixin, FormView)
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.utils.timezone import localtime
from ..models import User, UserGroup
from ..utils import user_add_success_next
from .. import forms

from ..utils import AdminUserRequiredMixin, UserRequiredMixin

class UserListView(AdminUserRequiredMixin, TemplateView):
    template_name = 'users/user_list.html'

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context.update({
            'app': _('用户'),
            'action': _('用户列表'),
        })
        return context

class UserForbiddenView(UserRequiredMixin, TemplateView):
    template_name = '403.html'

    def get_context_data(self, **kwargs):
        context = super(UserForbiddenView, self).get_context_data(**kwargs)
        context.update({
            'app': _('用户'),
            'action': _('访问拒绝'),
        })
        return context


class UserUserListJson(AdminUserRequiredMixin, BaseDatatableView):
    model = User
    columns = ["id", "username", "name", "phone", "email", "is_active",
               "id", "groups", "role", "department", "created_by", "date_expired", "comment"]
    order_columns = ["id", "username", "name", "phone", "email", "is_active", 
                     "id", "groups", "role", "department", "created_by", "date_expired", "comment"]
    page_length = 10

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'username':
            return super(UserUserListJson, self).render_column(row, column)
        elif column == 'date_expired':
            return str(localtime(row.date_expired).replace(tzinfo=None))
        elif column == 'groups':
            groups =  ''
            count = 0 
            for group in row.groups.values():
                if count == 0 :
                    groups = group['name'] 
                    count += 1
                else: 
                    groups = groups + ", " + group['name'] 
                    count += 1
            return groups
        elif column == 'is_active' :
            if getattr(row, column):
                return "enable"
            else:
                return "disable"
        else:
            #return row.__getattribute__(column)
            return getattr(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'sSearch', None)
        if search:
           qs = qs.filter(Q(username__icontains=search) |
                          Q(name__icontains=search) |
                          Q(phone__icontains=search) |
                          Q(email__icontains=search) |
                          Q(wechat__icontains=search) |
                          Q(dingtalk__icontains=search))
        return qs


class UserDetailView(AdminUserRequiredMixin, DetailView):
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = "user_object"

    def get_context_data(self, **kwargs):
        groups = UserGroup.objects.exclude(id__in=self.object.groups.all())
        context = {
            'app': _('用户'),
            'action': _('用户详情'),
            'groups': groups
        }
        kwargs.update(context)
        return super(UserDetailView, self).get_context_data(**kwargs)

class UserCreateView(AdminUserRequiredMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = forms.UserCreateUpdateForm
    template_name = 'users/user_create.html'
    success_url = reverse_lazy('users:user-list')
    success_message = _('<a href="{url}">{name}</a>')

    def get_context_data(self, **kwargs):
        context = super(UserCreateView, self).get_context_data(**kwargs)
        context.update({'app': _('用户'), 'action': _('创建用户')})
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.created_by = self.request.user.username or 'System'
        password = self.request.POST.get('password', '')
        if password:
            user.set_password(password)
        user.save()
        user_add_success_next(user)
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        url = reverse_lazy('users:user-detail', kwargs={'pk': self.object.pk})
        return self.success_message.format(
            url=url, name=self.object.name
        )

class UserUpdateView(AdminUserRequiredMixin, UpdateView):
    model = User
    form_class = forms.UserCreateUpdateForm
    template_name = 'users/user_update.html'
    context_object_name = 'user_object'
    success_url = reverse_lazy('users:user-list')

    def form_valid(self, form):
        username = self.object.username
        user = form.save(commit=False)
        user.username = username
        user.save()
        password = self.request.POST.get('password', '')
        if password:
            user.set_password(password)
        return super(UserUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        context.update({'app': _('用户'), 'action': _('更新用户')})
        return context