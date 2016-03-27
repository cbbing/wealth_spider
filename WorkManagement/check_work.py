#coding:utf8

import pandas as pd
import numpy as np
"""
考勤转换程序
*auther: bbchen
*date: 2016-03-02 14:13:27
"""

df_user = pd.read_excel('Data/users.xlsx')
print df_user.head()
name_to_id = {}
for ix, row in df_user.iterrows():
    name_to_id[row['name']]=row['id']
print name_to_id

df = pd.read_excel('Data/20160325.xls', sheetname=u'异常统计',skiprows=[0,1])
df = df.rename(columns={u'第一时段':u'上班', u'Unnamed: 5':u"下班"})

# print df.columns
# print df.head()

df = df[[u'姓名', u'日期', u'上班', u'下班']]
print df.columns
print df.head()


print ','.join(df_user['name'].get_values())

df = df[df[u'姓名'].apply(lambda name : name in df_user['name'].get_values())]
print df

df = df.replace(np.nan, '00:00')
print df

# 9:30上班的转成8:30
df[u'上班'] = df[u'上班'].apply(lambda x : int(x.split(":")[0]) *60 + int(x.split(":")[1]) )
df[u'下班'] = df[u'下班'].apply(lambda x : int(x.split(":")[0]) *60 + int(x.split(":")[1]))
print df
for ix, row in df.iterrows():
    print df.ix[ix, u'日期']
    print row
    if df.ix[ix, u'日期'] < '2016-03-14':
        if df.ix[ix, u'上班'] > 8*60+30 and df.ix[ix, u'下班'] > 18*60+30:
            df.ix[ix, u'上班'] -= 60
            df.ix[ix, u'下班'] -= 60
    else:
        if df.ix[ix, u'上班'] > 8*60+30:
            df.ix[ix, u'上班'] -= 30
            if df.ix[ix, u'下班'] > 8*60+30:
                df.ix[ix, u'下班'] -= 30

    if df.ix[ix, u'上班'] > 8*60+30 and df.ix[ix, u'上班'] < 8*60+36:
        df.ix[ix, u'上班'] -= 5

print df

# 补齐打卡
for ix, row in df.iterrows():
    if row[u'上班']== 0 and row[u'下班'] > 0:
        df.ix[ix, u'上班'] = 8*60 + 30
    elif row[u'上班']> 0 and row[u'下班'] == 0:
        df.ix[ix, u'下班'] = 17*60 + 30
print df

#日期转成2016/2/29格式
def f(x):
    ls = x.split('-')
    return "{}/{}/{}".format(int(ls[0]),int(ls[1]),int(ls[2]))
df[u'日期'] = df[u'日期'].apply(lambda x : f(x))
print df

df1 = df[[u'姓名',u'日期',u'上班']]
df2 = df[[u'姓名',u'日期',u'下班']]
# df1 = df1.replace(np.nan, '08:30')
# df2 = df2.replace(np.nan, '17:30')

df1.rename(columns={u'上班':u'时间'}, inplace=True)
df2.rename(columns={u'下班':u'时间'}, inplace=True)
df = pd.merge(df1,df2, how='outer')



#添加域账号
df[u'域账号'] = df[u'姓名'].apply(lambda x : name_to_id[x])
df = df.sort_index(by=[u'域账号',u'日期'])
print df
df[u'时间'] = df[u'时间'].apply(lambda x : "%d%d%d" % (x/60, x%60/10, (x%60)%10))
df[u'备注'] = ''
df = pd.DataFrame(df,columns = [u'姓名', u'域账号', u'日期',u'时间',u'备注'])
#df.rei(columns= [u'姓名', u'域账号', u'日期', u'下班'], inplace=True)

print df

df.to_excel('Data/result.xlsx', index=False)
df = df[df[u'时间'].apply(lambda x : True if x != '000' else False)]
df.to_excel('Data/result1.xlsx', index=False)
