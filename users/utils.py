# ~*~ coding: utf-8 ~*~

from __future__ import unicode_literals
from django.contrib.auth.mixins import UserPassesTestMixin
from common.utils import reverse
from common.tasks import send_mail_async
from django.utils.translation import ugettext as _
from django.conf import settings
import logging


logger = logging.getLogger('nms')

class AdminUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        elif not self.request.user.is_superuser:
            self.raise_exception = True
            return False
        return True

class UserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return True


def user_add_success_next(user):
    subject = _('帐号创建成功')
    recipient_list = [user.email]
    message = _("""
    您好 %(name)s:
    </br>
    您的帐号已经创建成功。
    </br>
    <a href="%(rest_password_url)s?token=%(rest_password_token)s">点击些链接设置登录密码</a>
    </br>
    此链接一小时内有效, 已经失效？ <a href="%(forget_password_url)s?email=%(email)s">重新发起请求</a>

    </br>
    ---

    </br>
    <a href="%(login_url)s">登录</a>

    </br>
    """) %{
        'name': user.name,
        'rest_password_url': reverse('users:reset-password', external=True),
        'rest_password_token': user.generate_reset_token(),
        'forget_password_url': reverse('users:forgot-password', external=True),
        'email': user.email,
        'login_url': reverse('users:login', external=True)
    }

    send_mail_async.delay(subject, message, recipient_list, html_message=message)

def send_reset_password_mail(user):
    subject = _('重置密码')
    recipient_list = [user.email]
    message = _("""
    Hello %(name)s:
    </br>
    Please click the link below to reset your password, if not your request, concern your account security
    </br>
    <a href="%(rest_password_url)s?token=%(rest_password_token)s">Click here reset password</a>
    </br>
    This link is valid for 1 hour. After it expires, <a href="%(forget_password_url)s?email=%(email)s">request new one</a>

    </br>
    ---

    </br>
    <a href="%(login_url)s">Login direct</a>

    </br>
    """) % {
        'name': user.name,
        'rest_password_url': reverse('users:reset-password', external=True),
        'rest_password_token': user.generate_reset_token(),
        'forget_password_url': reverse('users:forgot-password', external=True),
        'email': user.email,
        'login_url': reverse('users:login', external=True),
    }
    print(message)
    if settings.DEBUG:
        logger.debug(message)

    send_mail_async.delay(subject, message, recipient_list, html_message=message)