from __future__ import unicode_literals
import logging
import uuid
from django.db import models
from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _

__all__ = ['IDC']
logger = logging.getLogger(__name__)

class IDC(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=32, verbose_name=_('名称'))
    bandwidth = models.CharField(
        max_length=32, blank=True, verbose_name=_('带宽'))
    contact = models.CharField(
        max_length=128, blank=True, verbose_name=_('联系人'))
    phone = models.CharField(max_length=32, blank=True,
                             verbose_name=_('电话'))
    address = models.CharField(
        max_length=128, blank=True, verbose_name=_("地址"))
    intranet = models.TextField(blank=True, verbose_name=_('内网'))
    extranet = models.TextField(blank=True, verbose_name=_('外网'))
    date_created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_('创建日期'))
    operator = models.CharField(
        max_length=32, blank=True, verbose_name=_('运营商'))
    created_by = models.CharField(
        max_length=32, blank=True, verbose_name=_('创建者'))
    comment = models.TextField(blank=True, verbose_name=_('备注'))

    def __unicode__(self):
        return self.name
    __str__ = __unicode__

    @classmethod
    def initial(cls):
        return cls.objects.get_or_create(name=_('默认'), created_by=_('系统'), comment=_('默认机房'))[0]

    class Meta:
        ordering = ['name']
        verbose_name = _("机房")

    def get_absolute_url(self):
        return reverse('assets:IDC-detail', args=(self.pk,))

    @classmethod
    def generate_fake(cls, count=5):
        from random import seed, choice
        import forgery_py
        from django.db import IntegrityError

        seed()
        for i in range(count):
            IDC = cls(name="机房" + str(i),
                      bandwidth='200M',
                      contact=forgery_py.name.full_name(),
                      phone=forgery_py.address.phone(),
                      address=forgery_py.address.city() + forgery_py.address.street_address(),
                      operator=choice(['北京联通', '北京电信', 'BGP全网通', '广东电信']),
                      comment=forgery_py.lorem_ipsum.sentence(),
                      created_by='Fake')
            try:
                IDC.save()
                logger.debug('Generate fake asset group: %s' % IDC.name)
            except IntegrityError:
                print('Error continue')
                continue