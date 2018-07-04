# !/usr/bin/env python
''' common utils '''
from django.shortcuts import reverse as dj_reverse
from django.utils import timezone
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer, JSONWebSignatureSerializer, \
    BadSignature, SignatureExpired

SECRET_KEY = settings.SECRET_KEY

def reverse(view_name, urlconf=None, args=None, kwargs=None,
            current_app=None, external=False):
    url = dj_reverse(view_name, urlconf=urlconf, args=args,
                     kwargs=kwargs, current_app=current_app)

    if external:
        url = settings.SITE_URL.strip('/') + url
    return url

def get_object_or_none(model, **kwargs):
    try:
        obj = model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None
    return obj

def date_expired_default():
    ''' default expired days '''
    try:
        years = int(settings.CONFIG.DEFAULT_EXPIRED_YEARS)
    except TypeError:
        years = 70
    return timezone.now() +  timezone.timedelta(days=365*years)


class Signer(object):
    """用来加密,解密,和基于时间戳的方式验证token"""
    def __init__(self, secret_key=SECRET_KEY):
        self.secret_key = secret_key

    def sign(self, value):
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        s = JSONWebSignatureSerializer(self.secret_key)
        return s.dumps(value)

    def unsign(self, value):
        s = JSONWebSignatureSerializer(self.secret_key)
        try:
            return s.loads(value)
        except BadSignature:
            return {}

    def sign_t(self, value, expires_in=3600):
        s = TimedJSONWebSignatureSerializer(self.secret_key, expires_in=expires_in)
        return str(s.dumps(value), encoding="utf8")

    def unsign_t(self, value):
        s = TimedJSONWebSignatureSerializer(self.secret_key)
        try:
            return s.loads(value)
        except (BadSignature, SignatureExpired):
            return {}

signer = Signer()


def setattr_bulk(seq, key, value):
    def set_attr(obj):
        setattr(obj, key, value)
        return obj
    return map(set_attr, seq)