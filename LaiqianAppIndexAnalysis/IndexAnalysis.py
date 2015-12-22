#-*- coding:utf8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import pandas as pd
import matplotlib.pyplot as plt
import re
import tushare as ts

class IndexAnalysis:

    def __init__(self):

        self.dir_data = '../Data/YouMeng/'

        # 上证指数
        self.df_sh = pd.read_csv(self.dir_data+  'sh_20150101_20151218.csv')



    # 日活跃度与上证指数的相关性
    def day_activity(self):
        pass
        # trick to get the axes
        #fig, ax = plt.subplots()

        # 绘制上证指数
        values_date = map(lambda x : x[5:], self.df_sh['date'])
        values_sh = self.df_sh['close'].get_values()
        #ax.plot(values_sh, label='sh', color="b", linewidth=1)

        # 绘制日活
        file_name = '来钱_日_活跃用户_20150101_20151221'
        df_activity_android = pd.read_excel(self.dir_data + file_name +'.xls', 'Sheet1')
        df_activity_android = df_activity_android.reindex(df_activity_android.index[::-1])
        df_activity_android[u'日期'] = df_activity_android[u'日期'].map(lambda x : self.date_convert(x))
        print df_activity_android[:10]

        # 日留存率
        file_name = '来钱_日_留存用户_20150101_20151221'
        df_keep_android = pd.read_excel(self.dir_data + file_name +'.xls', 'Sheet1')
        df_keep_android[u'首次使用时间'] = df_keep_android[u'首次使用时间'].map(lambda  x : str(x)[5:10])
        #df_keep_android[u'日期'] = df_keep_android[u'日期'].map(lambda x : self.date_convert(x))
        print df_keep_android[:10]

        # 筛选日期
        values_bool = [d in values_date for d in df_activity_android[u'日期'].get_values()]
        print '{},{}'.format(len(df_activity_android), len(values_bool))
        df_activity_android = df_activity_android[values_bool]
        values_bool_keep = [d in values_date for d in df_keep_android[u'首次使用时间'].get_values()]
        df_keep_android = df_keep_android[values_bool_keep]
        print len(df_activity_android)
        print df_activity_android[:10]
        print df_keep_android[-10:][u'30天后留存率']
        #ax.plot(df_activity_android['活跃用户'].get_values(), label='day-activity', color="r", linewidth=1)

        # df_activity_android.index = values_date
        # df_activity_android[[u'android活跃用户',u'ios活跃用户']].plot(xticks=range(0, len(df_keep_android), 10),
        #                                                                 rot=90,
        #                                                                 subplots=True
        #                                                                 )
        #
        # df_keep_android.index = values_date
        # #`df_keep_android[[u'1天后留存率',u'7天后留存率',u'30天后留存率']].plot(xticks=range(0, len(df_keep_android), 10), rot=90, subplots=True)
        #
        # df_keep_android[[u'1天后留存率ios',u'7天后留存率ios',u'30天后留存率ios']].plot(xticks=range(0, len(df_keep_android), 10),
        #                                                                 rot=90,
        #                                                                 subplots=True
        #                                                                 )

        df = pd.DataFrame({'上证指数':values_sh,
                           '日活跃数':df_activity_android[u'活跃用户'].get_values(),
                           '新增用户':df_keep_android[u'新用户'].get_values(),
                           '1天后留存率':df_keep_android[u'1天后留存率'].get_values(),
                           '7天后留存率':df_keep_android[u'7天后留存率'].get_values(),
                           '14天后留存率':df_keep_android[u'14天后留存率'].get_values(),
                           '30天后留存率':df_keep_android[u'30天后留存率'].get_values(),

                           },
                          columns=['上证指数',
                                   '日活跃数',
                                   '新增用户',
                                   '1天后留存率',
                                   '7天后留存率',
                                   '14天后留存率',
                                   '30天后留存率'
                                   ])
        df.index = values_date
        #df[['上证指数','日活跃数']].plot(xticks=range(0, len(df), 10), rot=90, kind='area')
        #df[['上证指数','新增用户']].plot(xticks=range(0, len(df), 10), rot=90, kind='area')

        #df.plot(xticks=range(0, len(df), 10), rot=90, subplots=True, layout=(4,2))

        values_corr = df.corr()['上证指数']
        print values_corr

        returns_sh = df['上证指数'].pct_change()
        cumprod_sh = (1+returns_sh).cumprod()
        cumprod_sh[0] = 1  #将第一个值设置为1

        returns_activity = df['日活跃数'].pct_change()
        cumprod_activity = (1+returns_activity).cumprod()
        cumprod_activity[0] = 1  #将第一个值设置为1

        returns_new = df['新增用户'].pct_change()
        cumprod_new = (1+returns_new).cumprod()
        cumprod_new[0] = 1  #将第一个值设置为1


        df['上证指数累计增长率'] = cumprod_sh
        df['日活跃数累计增长率'] = cumprod_activity
        df['新增用户累计增长率'] = cumprod_new
        print df[:10]
        df[['上证指数累计增长率', '日活跃数累计增长率']].plot(xticks=range(0, len(df), 10), rot=90)
        df[['上证指数累计增长率', '新增用户累计增长率']].plot(xticks=range(0, len(df), 10), rot=90)
        #df[1:][['上证指数增长率','日活跃数增长率','新增用户增长率']].plot(xticks=range(0, len(df), 10), rot=90, kind='area')

        values_corr = df['上证指数累计增长率'].corr(df['日活跃数累计增长率'])
        print values_corr
        values_corr = df['上证指数累计增长率'].corr(df['新增用户累计增长率'])
        print values_corr

        # zValues = cwavelet.getWaveletData(xValues, 'db2', 2, 'sqtwolog')
        # zxValue = np.arange(0,len(zValues),1)
        #plt.figure(figsize=(16,8))

        #ax.plot(zxValue, zValues, color="b", linewidth=2)
        #ax.grid()

        # make ticks and tick labels
        # xticks = range(0, len(values_date)+1,10)
        # xticklabels= values_date[::10]

        #set ticks and tick labels
        # ax.set_xticks(xticks)
        # ax.set_xticklabels(xticklabels,rotation=15)

        #plt.legend()
        plt.show()


    def month_activity(self):
        df_sh = ts.get_hist_data('sh', start='2015-01-01', end='2015-12-18', ktype='M')
        df_sh = df_sh.reindex(df_sh.index[::-1])
        print len(df_sh)

        # 上证指数
        print df_sh
        values_date = map(lambda x : str(x)[5:7], df_sh.index)
        values_sh = df_sh['close'].get_values()
        print values_sh

        # 月活
        file_name = '来钱_月_活跃用户_20150101_20151222'
        df_activity = pd.read_excel(self.dir_data + file_name +'.xls', 'Sheet1')
        df_activity = df_activity.reindex(df_activity.index[::-1])
        print df_activity

        # 月新增
        file_name = '来钱_月_新增用户_20150101_20151222'
        df_keep = pd.read_excel(self.dir_data + file_name +'.xls', 'Sheet1')
        df_keep = df_keep.reindex(df_keep.index[::-1])
        print df_keep

        df = pd.DataFrame({'上证指数':values_sh,
                           '月活跃数':df_activity['ActiveUser'].get_values(),
                           '月新增用户':df_keep['NewUser'].get_values()
                           },
                          columns=['上证指数',
                                   '月活跃数',
                                   '月新增用户',

                                   ])
        df.index = values_date

        df['上证指数变化率'] = df['上证指数'].pct_change()
        df['月活跃数变化率'] = df['月活跃数'].pct_change()
        df['月新增用户变化率'] = df['月新增用户'].pct_change()
        df.ix['01', ['上证指数变化率','月活跃数变化率','月新增用户变化率']] = 0
        print df[['上证指数变化率','月活跃数变化率','月新增用户变化率']]

        df_2_9 = df.reindex(['0' + str(i) for i in range(2,10)])
        df_9_11 = df.reindex(['09', '10', '11'])
        print df_2_9
        print df_9_11

        df_2_9[['上证指数','月活跃数','月新增用户']].plot(xticks=range(0, len(df_2_9), 1), rot=0, kind='line', subplots=True)
        df_2_9[['月活跃数','月新增用户']].plot(xticks=range(0, len(df_2_9), 1), rot=0, kind='line', subplots=True)

        df_9_11[['上证指数','月活跃数','月新增用户']].plot(xticks=range(0, len(df_9_11), 1), rot=0, kind='line', subplots=True)
        df_9_11[['月活跃数','月新增用户']].plot(xticks=range(0, len(df_9_11), 1), rot=0, kind='line', subplots=True)

        corr_2_9 = df_2_9.corr()
        corr_9_11 = df_9_11.corr()
        print corr_2_9, '\n', corr_9_11

        #df[['上证指数','月活跃数','月新增用户']].plot(xticks=range(0, len(df), 1), rot=90, kind='line', subplots=True)
        #df[['上证指数变化率','月活跃数','月新增用户']].plot(xticks=range(0, len(df), 1), rot=90, kind='line', subplots=True)
        #df[['上证指数变化率','月活跃数变化率','月新增用户变化率']].plot(xticks=range(0, len(df), 1), rot=90, kind='line', subplots=True)
        #df[['上证指数','月新增用户']].plot(xticks=range(0, len(df), 1), rot=90, kind='line', subplots=True)

        returns_sh = df['上证指数'].pct_change()
        cumprod_sh = (1+returns_sh).cumprod()
        cumprod_sh[0] = 1  #将第一个值设置为1

        returns_activity = df['月活跃数'].pct_change()
        cumprod_activity = (1+returns_activity).cumprod()
        cumprod_activity[0] = 1  #将第一个值设置为1

        returns_new = df['月新增用户'].pct_change()
        cumprod_new = (1+returns_new).cumprod()
        cumprod_new[0] = 1  #将第一个值设置为1


        df['上证指数累计增长率'] = cumprod_sh
        df['月活跃数累计增长率'] = cumprod_activity
        df['月新增用户累计增长率'] = cumprod_new

        #df[['上证指数累计增长率', '月活跃数累计增长率','月新增用户累计增长率']].plot(xticks=range(0, len(df), 1), rot=90, subplots=True)
        #df[['上证指数累计增长率', '月活跃数','月新增用户']].plot(xticks=range(0, len(df), 1), rot=90, subplots=True)

        values_corr = df.corr()['上证指数变化率']
        print values_corr

    def date_convert(self, date_cn):

        dates = re.findall('\d+', date_cn)
        if len(dates) == 2:
            month, day = dates
            if len(month) == 1:
                month = '0' + month
            if len(day) == 1:
                day = '0' + day
            date_cn = month + '-' + day
        return date_cn



if __name__ == '__main__':
    indexAnalysis = IndexAnalysis()
    indexAnalysis.month_activity()
