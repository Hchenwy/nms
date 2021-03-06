"""nms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls import include
from .views import IndexView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),

    url(r'^users/', include('users.urls.views_urls',  namespace='users')),
    url(r'^assets/', include('assets.urls.views_urls',  namespace='assets')),
    url(r'^perms/', include('perms.urls.views_urls', namespace='perms')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^nodes/', include('zabbix.urls')),
    url(r'^alert/', include('alert.urls')),

    # Api url view map
    url(r'^api/users/', include('users.urls.api_urls', namespace='api-users')),
    url(r'^api/assets/', include('assets.urls.api_urls', namespace='api-assets')),
    url(r'^api/perms/', include('perms.urls.api_urls', namespace='api-perms')),
]

