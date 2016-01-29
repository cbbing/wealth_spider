#coding:utf8

import pandas as pd

def keys_finance():
    """
    类别说明：1：金融，0：非金融，2：待定
    :return:
    """
    dfs_fin = []
    dfs_other = []
    df_dict = pd.read_excel('Data/关键词统计.xlsx', sheetname=None, na_values=-1) # sheetname=None, 获取所有工作表
    for sheetname, df in df_dict.iteritems():
        if u'类别' not in df.columns.get_values():
            continue

        df_fin = df[df[u'类别'] == 1]
        df_other = df[df[u'类别'] == 0]
        df_fin[u'分类'] = sheetname
        df_other[u'分类'] = sheetname

        dfs_fin.append(df_fin)
        dfs_other.append(df_other)

    df_fin_all = pd.concat(dfs_fin, ignore_index=True)
    df_other_all = pd.concat(dfs_other, ignore_index=True)
    df_fin_all = df_fin_all[[u'关键词', u'计数',u'分类', u'类别']]
    df_other_all = df_other_all[[u'关键词', u'计数', u'分类', u'类别']]
    print df_fin_all.head()
    print len(df_fin_all), ":", len(df_other_all)
    df_fin_all.to_excel('Data/keys_fin.xlsx', index=False)
    df_other_all.to_excel('Data/keys_other.xlsx', index=False)


keys_finance()