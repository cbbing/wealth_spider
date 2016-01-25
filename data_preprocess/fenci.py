#coding=utf8

# 分词
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import re
import jieba
jieba.load_userdict('../Data/userdict2.txt')
import jieba.analyse

#jieba.enable_parallel(2)

import pickle
import time
from nltk import FreqDist
from tqdm import tqdm
from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing
from tomorrow import threads
import threading
import pandas as pd
from pandas import DataFrame

from util.helper import fn_timer
import matplotlib.pyplot as plt


classifies = [u'美股', u'国内财经', u'证券', u'国际财经',  u'期货', u'外汇', u'港股', u'产经', u'基金']
f = open('../Data/stopwords.txt','r')
stopwords = f.read().split('\n')
f.close()

def fenci(data):

    data = re.compile(r'\s+').sub('', data)
    data = re.compile(r'\!\[.*?\]\(.*?\)').sub('', data)

    seg_list = jieba.cut(data)

    # 基于TF-IDF算法的关键词抽取
    tags = jieba.analyse.extract_tags(data, topK=50)
    print ','.join(tags)

    # 基于TextRank算法的关键词抽取
    tags2 = jieba.analyse.textrank(data, topK=50)
    print ','.join(tags2)


    fdist = FreqDist([seg for seg in seg_list])
    fdist.plot(50)

@fn_timer
def test_sina_finance():

    #创建锁
    #mutex = threading.Lock()

    @fn_timer
    def get_dataframe():
        import pandas as pd
        from db_config import engine, mysql_table_sina_finance
        #sql = "select title, content from {table} where classify='{classify}' limit 0,10".format(table=mysql_table_sina_finance, classify=classify)
        sql = "select * from {table}".format(table=mysql_table_sina_finance)
        df = pd.read_sql(sql, engine)
        return df

    df_all = get_dataframe()
    print df_all.head()
    for i in range(0,len(classifies)):

        df = df_all[df_all['classify']==classifies[i]]
        #df = df[:1000]
        indexs = range(0, len(df))
        print classifies[i], 'df length:{}'.format(len(indexs))
        df.index = indexs
        if len(df) == 0:
            continue

        df['keys'] = ''
        df['tags'] = ''
        #print df.head()

        t0 = time.time()
        pool = multiprocessing.Pool(processes = 4)
        #pool = ThreadPool(processes = 8)
        result = []
        contents = []
        for ix, row in df.iterrows():
            try:
                content = row['title']
                if row['content']:
                    content += " " + row['content']
                contents.append(content)
            except Exception,e:
                None
            #result.append(pool.apply(get_one_article_keys, (content,)))
        results = pool.map(get_one_article_keys, contents)
        pool.close()
        pool.join()
        t1 = time.time()
        print 'time pass:{:.3f}'.format(t1-t0)

        #keys_list = []
        tag_list = []
        for tag in results:
            tag_list.extend(tag.strip().split(','))

        # print len(keys_list)
        # fdist = FreqDist(keys_list)
        # print len(fdist.keys())
        # f = file('fdist_{}.pkl'.format(i), 'wb')
        # pickle.dump(fdist, f)
        # f.close()

        fdist_tag = FreqDist(tag_list)
        #print len(fdist_tag.keys())
        f = file('Data/ftags_{}.pkl'.format(i), 'wb')
        pickle.dump(fdist_tag, f)
        f.close()

def get_one_article_keys(content):
    try:


        tags2 = jieba.analyse.textrank(content, topK=50)
        tag_each = [tag.strip() for tag in tags2  if (len(tag.strip()) > 0 and tag.strip() not in stopwords)]
        #print multiprocessing.current_process()
        return ','.join(tag_each)
    except Exception,e:
        print "get_one_article_keys():%s" % str(e)
        return ''


#文件名: ch.py
def set_ch():
    from pylab import mpl
    mpl.rcParams['font.sans-serif'] = ['FangSong'] # 指定默认字体
    mpl.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题

set_ch()

def test_fenci():

    dfs = []

    for i in range(0, 9):
        f = file('Data/ftags_{}.pkl'.format(i), 'rb')
        fdist = pickle.load(f)
        #fdist.plot(50)
        df = DataFrame(fdist.items(), columns=['关键词', '计数'])
        df = df.sort_index(by='计数', ascending=False)
        df.index = range(len(df))

        df_plt = df[:30]
        df_plt = df_plt[::-1]
        #df_plt['关键词'].apply(lambda x : x.encode('utf8'))
        print df_plt.head()
        df_plt.plot(kind='barh', x=df_plt['关键词'], title=classifies[i])

        #plt.show()

        filePath = 'Data/{}.png'.format(classifies[i])
        str_name_f = filePath.decode("utf8")
        plt.savefig(str_name_f, dpi=100)

        dfs.append((classifies[i],df))

        #print df[df[1] > 1]
        f.close()
    print 'end'

    with pd.ExcelWriter('keys.xlsx') as writer:
        for key, df in dfs:
            print key
            df.to_excel(writer, sheet_name=key, index=False)

if __name__ == "__main__":
    print 'begin'
    # test_sent = (
    #     "李小福是创新办主任也是云计算方面的专家; 什么是八一双鹿\n"
    #     "例如我输入一个带“韩玉赏鉴”的标题，在自定义词库中也增加了此词为N类\n"
    #     "「台中」正確應該不會被切開。mac上可分出「石墨烯」；此時又可以分出來凱特琳了。"
    #     )
    # words = jieba.cut(test_sent)
    # print('/'.join(words))
    #test_sina_finance()
    test_fenci()

    #f = open('../Data/weixin.md')
    #fenci(f.read())