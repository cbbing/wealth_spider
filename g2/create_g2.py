#coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import pandas as pd
import json

def gen_map():
    df = pd.read_excel('data/zqgs.xlsx')
    grouped = df['name'].groupby(df['area'])
    se_counts = grouped.count()

    zq_list = []
    for ix, value in se_counts.iteritems():
        print ix, value
        zq_d = {'name':ix, 'value':value}
        zq_list.append(zq_d)

    encodejson = json.dumps(zq_list)
    print repr(zq_list)
    print encodejson

    f = open('html/broker-area-raw.html','r')
    data = f.read()
    print data
    data = data.replace('python_userData', encodejson)
    print data
    f.close()
    f = open('html/broker-area.html', 'w')
    f.write(data)
    f.close()


gen_map()