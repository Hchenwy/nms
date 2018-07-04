# -*- coding:utf8 -*-
# 
  
import datetime
import random
from pyecharts import HeatMap
from pyecharts import Bar
from pyecharts import TreeMap

def Heatmap():
    begin = datetime.date(2017, 1, 1)
    end = datetime.date(2017, 12, 31)
    data = [[str(begin + datetime.timedelta(days=i)),
            random.randint(1000, 25000)] for i in range((end - begin).days + 1)]
    heatmap = HeatMap("报警热力图", "最近一年报警情况", width=1100)
    heatmap.add("", data, is_calendar_heatmap=True,
                visual_text_color='#000', visual_range_text=['', ''],
                visual_range=[1000, 25000], calendar_cell_size=['auto', 30],
                is_visualmap=True, calendar_date_range="2017",
                visual_orient="horizontal", visual_pos="center",
                visual_top="80%", is_piecewise=True)
    return heatmap

def Barmap():
    attr = ["web", "存储", "数据库", "管理", "测试", "运营"]
    v1 = [5, 20, 36, 10, 75, 90]
    v2 = [10, 25, 8, 60, 20, 80]
    bar = Bar("故障与恢复", width=1200, height=410)
    bar.add("故障", attr, v1, mark_line=["min", "max"])
    bar.add("恢复", attr, v2, mark_line=["min", "max"])
    return bar


def Treemap():
    treemap = TreeMap("树图示例", width=1200, height=600)
    import json
    with open("/root/nms_lqx/nms_dev/static/json/treemap-drill-down.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    treemap.add("演示数据", data, is_label_show=True, label_pos='inside')
    return treemap


import random
import string



def children(pname):
    name = "".join(random.sample(string.ascii_letters, 5))
    value = random.randint(50,100)
    return {"value": value, "name": name, "path":pname + ":" + name}

def get_sumary_js():
    groups = ["存储节点", "管理节点", "计算节点", "Web", "数据库", "测试", "研发", "商用"]
    js=[]
    for name in groups:
        dict={}
        dict["name"]=name
        dict["path"]=name
        value=0
        childrens = []
        hosts_num=random.choice([x for x in range(20,50)])
        for _ in range(hosts_num):
            child  = children(name)
            value += child["value"]
            childrens.append(child)
        dict["children"] = childrens
        dict["value"] = value
        js.append(dict)
    return js
    
    
    