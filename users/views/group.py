# ~*~ coding: utf-8 ~*~
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.urls import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from ..models import User, UserGroup
from ..utils import AdminUserRequiredMixin
from .. import forms

class UserGroupListView(AdminUserRequiredMixin, TemplateView):
    template_name = 'users/user_group_list.html'

    def get_context_data(self, **kwargs):
        context = super(UserGroupListView, self).get_context_data(**kwargs)
        context.update({'app': _('用户组'), 'action': _('用户组列表')})
        return context

class UserGroupCreateView(AdminUserRequiredMixin, SuccessMessageMixin, CreateView):
    model = UserGroup
    form_class = forms.UserGroupForm
    template_name = 'users/user_group_create_update.html'
    success_url = reverse_lazy('users:user-group-list')
    success_message = '<a href={url}> {name} </a> was created successfully'

    def get_context_data(self, **kwargs):
        context = super(UserGroupCreateView, self).get_context_data(**kwargs)
        users = User.objects.all()
        context.update({'app': _('用户'), 'action': _('创建用户组'),
                        'users': users})
        return context

    # 需要添加组下用户, 而user并不是group的多对多,所以需要手动建立关系
    def form_valid(self, form):
        user_group = form.save()
        users_id_list = self.request.POST.getlist('users', [])
        users = User.objects.filter(id__in=users_id_list)
        user_group.created_by = self.request.user.username or 'Admin'
        user_group.users.add(*users)
        user_group.save()
        return super(UserGroupCreateView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        url = reverse_lazy('users:user-group-detail',
                           kwargs={'pk': self.object.id}
                           )
        return self.success_message.format(
            url=url, name=self.object.name
        )

class UserGroupDetailView(AdminUserRequiredMixin, DetailView):
    model = UserGroup
    context_object_name = 'user_group'
    template_name = 'users/user_group_detail.html'

    def get_context_data(self, **kwargs):
        users = User.objects.exclude(id__in=self.object.users.all())
        context = {
            'app': _('用户'),
            'action': _('用户组详情'),
            'users': users,
        }
        kwargs.update(context)
        return super(UserGroupDetailView, self).get_context_data(**kwargs)

class UserGroupListJson(BaseDatatableView):
    model = UserGroup
    columns = ["id", "name", "created_by", "comment", "date_created", "id"]
    order_columns = ["id", "name", "created_by", "comment", "date_created", "id"]
    page_length = 10

    def render_column(self, row, column):
        # We want to render user as a custom column
        user_count = 0
        if column == 'name':
            return super(UserGroupListJson, self).render_column(row, column)
        elif column == 'date_created':
            dt = row.date_created.replace(tzinfo=None)
            return str(dt)
        elif column == 'created_by':
            user_count = User.objects.filter(groups=row.id).count()
            return user_count
        else:
            return row.__getattribute__(column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'sSearch', None)
        if search:
           qs = qs.filter(name__icontains=search)
        return qs


class UserGroupUpdateView(AdminUserRequiredMixin, UpdateView):
    model = UserGroup
    form_class = forms.UserGroupForm
    template_name = 'users/user_group_create_update.html'
    success_url = reverse_lazy('users:user-group-list')

    def get_context_data(self, **kwargs):
        # self.object = self.get_object()
        context = super(UserGroupUpdateView, self).get_context_data(**kwargs)
        users = User.objects.all()
        group_users = [user.id for user in self.object.users.all()]
        context.update({
            'app': _('用户组'),
            'action': _('编辑用户组'),
            'users': users,
            'group_users': group_users
        })
        return context

    def form_valid(self, form):
        user_group = form.save()
        users_id_list = self.request.POST.getlist('users', [])
        users = User.objects.filter(id__in=users_id_list)
        user_group.users.clear()
        user_group.users.add(*users)
        user_group.save()
        return super(UserGroupUpdateView, self).form_valid(form)