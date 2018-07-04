#!/usr/bin/env python
# -*- coding: utf-8 -*-

from MySQLdb import connect, cursors

class Mysqlapi(object):
    def __init__(self, **kwargs):
        self.user = kwargs.get('user') or 'root'
        self.password = kwargs.get('password') or ''
        self.db = kwargs.get('db') or ''
        self.host = kwargs.get('host') or '127.0.0.1'
        self.port = int(kwargs.get('port')) or 3306
        self.cxn = connect(user=self.user, password=self.password, db=self.db, host=self.host, port=self.port, cursorclass=cursors.DictCursor, charset='utf8')
        self.cur = self.cxn.cursor()

    def select(self, table, **kwargs):
        join = where = order_by = limit = ''

        for key in kwargs:
            params = key.split("__")
            if key == 'order_by':
                if kwargs[key][0] == '-':
                    order_by = ' ORDER BY {tbl}.{param} DESC'.format(tbl=table, param=kwargs[key][1:])
                else:
                    order_by = ' ORDER BY {tbl}.{param} ASC'.format(tbl=table, param=kwargs[key])
            elif key == 'limit':
                limit = ' LIMIT {range}'.format(range=kwargs[key])
            elif key == 'join':
                if kwargs[key]:
                    join = ' ' + kwargs[key]
            elif key == 'join_condition':
                if kwargs[key]:
                    where += ' {condition} AND'.format(condition=kwargs[key])
            elif len(params) == 1:
                if isinstance(kwargs[key], list):
                    if kwargs[key]:
                        or_condition = ''
                        for value in kwargs[key]:
                            or_condition += ' {tbl}.{param} = {value} OR'.format(tbl=table, param=params[0], value=value)
                        where += ' ({condition}) AND'.format(condition=or_condition[:-3])
                    else: #如果参数列表为空，则不添加该过滤项
                        pass
                else:
                    where += ' {tbl}.{param} = {value} AND'.format(tbl=table, param=params[0], value=kwargs[key])
            elif len(params) == 2 and params[1] == 'icontains':
                where += ' {tbl}.{param} LIKE "%{value}%" AND'.format(tbl=table, param=params[0], value=kwargs[key])
            elif len(params) == 2 and params[1] == 'not':
                where += ' {tbl}.{param} <> {value} AND'.format(tbl=table, param=params[0], value=kwargs[key])

        sql = 'SELECT * FROM {tbl}{join} WHERE({where}){order_by}{limit}'.format(tbl=table, join=join, where=where[:-4], order_by=order_by, limit=limit)
        self.cur.execute(sql)
        return self.cur.fetchall()

    def select_count(self, table, **kwargs):
        return len(self.select(table, **kwargs))

    def get(self, table, **kwargs):
        result = self.select(table, **kwargs)
        if len(result) == 1:
            return result[0]
        else:
            return {}

    def __del__(self):
        try:
            self.cur.close()
            self.cxn.close()
        except

if __name__ == '__main__':
    mysqlapi = Mysqlapi(user='django', password='django', db='django', host='127.0.0.1')
    dict = mysqlapi.select('zabbix_items', join='INNER JOIN  zabbix_hosts ON (zabbix_items.hostid = zabbix_hosts.id)', join_condition='zabbix_hosts.hostid = 14258', name__icontains='', order_by='name', limit='2')
    print(dict)







