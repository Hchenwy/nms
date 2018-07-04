#!/usr/bin/env python
''' 用户模块 '''
import os
import uuid
from django.conf import settings
from collections import OrderedDict
from django.db import models
from django.shortcuts import reverse
from django.core import signing
from django.contrib.auth.models import  AbstractUser
from django.contrib.auth.hashers import make_password
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from common.utils import date_expired_default, signer
from simple_history.models import HistoricalRecords
from .group import UserGroup

__all__ = ['User']

class User(AbstractUser):
    '''扩展 AbstractUser 模块'''
    ROLE_CHOICES = (
        ('Admin', _('系统管理员')),
        ('User', _('普通用户')),
        ('Linkman', _('联系人')),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,verbose_name=_('ID'))
    username = models.CharField(max_length=20, unique=True, verbose_name=_('用户名'))
    name = models.CharField(max_length=20, verbose_name=_('姓名'))
    email = models.EmailField(max_length=30, unique=True, verbose_name=_('邮箱'))
    groups = models.ManyToManyField(UserGroup,
                                    related_name='users', blank=True,
                                    verbose_name=_('用户组'))
    role = models.CharField(choices=ROLE_CHOICES,
                            default='User', max_length=30, blank=True,
                            verbose_name=_('网管系统角色'))
    avatar = models.ImageField(upload_to="avatar", null=True, verbose_name=_('头像'))
    wechat = models.CharField(max_length=30, blank=True, verbose_name=_('微信'))
    dingtalk = models.CharField(max_length=30, blank=True, verbose_name=_('钉钉'))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('电话'))
    department = models.CharField(max_length=20,
                                  blank=True, null=True,
                                  verbose_name=_('部门'))
    position = models.CharField(max_length=20,
                                  blank=True, null=True,
                                  verbose_name=_('职位'))
    comment = models.TextField(max_length=200, blank=True, verbose_name=_('备注'))
    is_first_login = models.BooleanField(default=False)
    date_expired = models.DateTimeField(default=date_expired_default, blank=True, null=True,
                                        verbose_name=_('过期时间'))
    created_by = models.CharField(max_length=30, default='', verbose_name=_('创建人'))
    history = HistoricalRecords(excluded_fields=['is_first_login', 'create_by'])

    @property
    def password_raw(self):
        raise AttributeError('Password raw is not a readable attribute')

    #: Use this attr to set user object password, example
    #: user = User(username='example', password_raw='password', ...)
    #: It's equal:
    #: user = User(username='example', ...)
    #: user.set_password('password')
    @password_raw.setter
    def password_raw(self, password_raw_):
        self.set_password(password_raw_)

    def get_absolute_url(self):
        return reverse('users:user-detail', args=(self.pk,))

    @property
    def is_expired(self):
        if self.date_expired and self.date_expired < timezone.now():
            return True
        else:
            return False

    @property
    def is_valid(self):
        if self.is_active and not self.is_expired:
            return True
        return False

    @property
    def is_superuser(self):
        if self.role == 'Admin':
            return True
        else:
            return False

    @is_superuser.setter
    def is_superuser(self, value):
        if value is True:
            self.role = 'Admin'
        else:
            self.role = 'User'


    @property
    def is_staff(self):
        if self.is_authenticated and self.is_valid:
            return True
        else:
            return False

    @is_staff.setter
    def is_staff(self, value):
        pass

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.username

        super(User, self).save(*args, **kwargs)
        # Add the current user to the default group.
        if not self.groups.count():
            group = UserGroup.initial()
            self.groups.add(group)

    def is_member_of(self, user_group):
        if user_group in self.groups.all():
            return True
        return False

    def history_all(self):
        check_fileds = ['password', 'is_active', 'username', 'name', 'email',
                        'role', 'avatar', 'wechat', 'dingtalk', 'phone',
                        'department', 'position', 'comment',  'date_expired']
        historys = self.history.all()
        history_list =  []
        if len(historys) == 1:
            history_list =  [{"date": historys[0].history_date, "event": "创建用户"}]
            return history_list
        else :
            hin = historys[0]
            for hio in historys[1:10]:
                for i in check_fileds:
                    new_hi = str(hin.__getattribute__(i))
                    old_hi = str(hio.__getattribute__(i))
                    if i == "password" and new_hi != old_hi:
                        history_list.append({"date": hin.history_date, "event": "修改密码"})
                        continue
                    elif new_hi != old_hi:
                        item_name = self._meta.get_field(i).verbose_name
                        history_list.append({"date": hin.history_date, "event": '%s 由 "%s" 变更为 "%s"' %(item_name, old_hi, new_hi)})
                        continue
                    else:
                        continue
                hin = hio
            return history_list


    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatar')
            if os.path.isdir(avatar_dir):
                return os.path.join(settings.MEDIA_URL, 'avatar', 'default.png')
        return 'https://www.gravatar.com/avatar/c6812ab450230979465d7bf288eadce2a?s=120&d=identicon'

    def generate_reset_token(self):
        return signer.sign_t({'reset': str(self.pk), 'email': self.email}, expires_in=3600)

    @classmethod
    def validate_reset_token(cls, token):
        try:
            data = signer.unsign_t(token)
            user_id = data.get('reset', None)
            user_email = data.get('email', '')
            user = cls.objects.get(id=user_id, email=user_email)

        except (signing.BadSignature, cls.DoesNotExist):
            user = None
        return user

    def reset_password(self, new_password):
        self.set_password(new_password)
        self.save()

    def delete(self):
        if self.pk == 1 or self.username == 'admin':
            return
        return super(User, self).delete()

    class Meta:
        ordering = ['username']

    #: Use this method initial user
    @classmethod
    def initial(cls):
        user = cls(username='admin',
                   email='admin@nms.org',
                   name=_('Administrator'),
                   password_raw='admin',
                   role='Admin',
                   comment=_('Administrator is the super user of system'),
                   created_by=_('System'))
        user.save()
        user.groups.add(UserGroup.initial())

    @classmethod
    def generate_fake(cls, count=100):
        from random import seed, choice
        import forgery_py
        from django.db import IntegrityError

        seed()
        for i in range(count):
            user = cls(username=forgery_py.internet.user_name(True),
                       email=forgery_py.internet.email_address(),
                       name=forgery_py.name.full_name(),
                       password=make_password(forgery_py.lorem_ipsum.word()),
                       role=choice(list(User.ROLE_CHOICES)),
                       wechat=forgery_py.internet.user_name(True),
                       comment=forgery_py.lorem_ipsum.sentence(),
                       created_by="System fake")
            try:
                user.save()
            except IntegrityError:
                print('Duplicate Error, continue ...')
                continue
            user.groups.add(choice(UserGroup.objects.all()))
            user.save()
