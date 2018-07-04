# -*- coding: utf-8 -*-
'''用户登录信息处理'''
#

import ipaddress
import requests
from .models import LoginLog

def validate_ip(ip_address):
    '''判断ip合法性'''
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        print('valid error')
    return False


def write_login_log(username, name='', login_type='', login_ip='', user_agent=''):
    '''写入登录日志'''
    if not (login_ip and validate_ip(login_ip)):
        login_ip = '0.0.0.0'
    if not name:
        name = username
    login_city = get_ip_city(login_ip)
    LoginLog.objects.create(username=username, name=name, login_type=login_type,
                            login_ip=login_ip, login_city=login_city, user_agent=user_agent)


def get_ip_city(ip_address, timeout=10):
    '''获取ip所属城市'''
    # Taobao ip api: http://ip.taobao.com//service/getIpInfo.php?ip=8.8.8.8
    # Sina ip api: http://int.dpool.sina.com.cn/iplookup/iplookup.php?ip=8.8.8.8&format=json

    url = 'http://int.dpool.sina.com.cn/iplookup/iplookup.php?ip=%s&format=json' % ip_address
    try:
        response = requests.get(url, timeout=timeout)
    except requests.Timeout:
        response = None
    city = 'Unknown'
    if response and response.status_code == 200:
        try:
            data = response.json()
            if not isinstance(data, int) and data['ret'] == 1:
                city = data['country'] + ' ' + data['city']
        except ValueError:
            pass
    return city
