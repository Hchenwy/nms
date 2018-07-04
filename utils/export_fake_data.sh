#!/bin/bash
#
python /root/nms_lqx/nms_dev/manage.py shell <<EOF
from users.models.utils import *
default_admin = User.objects.filter(username="admin")
if not default_admin :
    admin=User(name="Leon", username="admin", role="Admin")
    admin.set_password("admin")
    admin.save()
from zabbix.models import Zabbix
zbx=Zabbix(name="测试13", zbx_user="admin", zbx_passwd="dVxUPN04UQNYTj4InNmV", zbx_ip="192.168.50.13", zbx_url="http://192.168.50.13/zabbix/api_jsonrpc.php")
zbx.save()

for init_group in ['项目用户组', '联系人组']:
    group=UserGroup.objects.filter(name=init_group)
    if not group:
        create_group=UserGroup(name=init_group,created_by='System', comment=init_group)
        create_group.save()
EOF
echo "DONE"
#python ../apps/manage.py dbshell << EOF
#delete from auth_permission;
#delete from django_content_type;
#EOF
#python ../apps/manage.py dumpdata > ../apps/fixtures/fake.json
#generate_fake()
#from assets.models.utils import *
#generate_fake()