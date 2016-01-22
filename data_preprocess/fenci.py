#coding=utf8

# 分词
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import re
import jieba
jieba.load_userdict('../Data/userdict1.txt')
import jieba.analyse

jieba.enable_parallel(2)

import pickle
from nltk import FreqDist
from tqdm import tqdm
from multiprocessing.dummy import Pool as ThreadPool
from tomorrow import threads
import threading

from util.helper import fn_timer




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
    mutex = threading.Lock()

    @fn_timer
    def get_dataframe():
        import pandas as pd
        from db_config import engine, mysql_table_sina_finance
        #sql = "select title, content from {table} where classify='{classify}' limit 0,10".format(table=mysql_table_sina_finance, classify=classify)
        sql = "select * from {table} limit 0, 40000".format(table=mysql_table_sina_finance)
        df = pd.read_sql(sql, engine)
        return df

    def _get_one_article_keys(ix):
        try:
            row = df.loc[ix]
            content = row['title'] + " " + row['content']
            # seg_list = jieba.cut(content)
            # keys_each = [seg.strip() for seg in seg_list if (len(seg.strip()) > 0 and seg.strip() not in stopwords)]

            tags2 = jieba.analyse.textrank(content, topK=50)
            tag_each = [tag.strip() for tag in tags2  if (len(tag.strip()) > 0 and tag.strip() not in stopwords)]
            print row['time']
            # df.loc[ix, 'keys'] = ','.join(keys_each)
            # df.loc[ix,'tags'] = ','.join(tag_each)
            #df['keys'][ix] = ','.join(keys_each)
            df['tags'][ix] = ','.join(tag_each)
            #print df.loc[ix, 'keys']
            #return  (keys_each, tag_each)
            #if mutex.acquire(): #锁定
            #keys_list.extend(keys_each)
            #tag_list.extend(tag_each)
            #mutex.release()
        except Exception,e:
            print "_get_one_article_keys():%s" % str(e)
            #return ([],[])

    f = open('../Data/stopwords.txt','r')
    stopwords = f.read().split('\n')
    classifies = ['美股', '国内财经', '证券', '国际财经',  '期货', '外汇', '港股', '产经', '基金']
    df_all = get_dataframe()
    print df_all.head()
    for i in range(0,len(classifies)):

        df = df_all[df_all['classify']==classifies[i]]
        df = df[:1000]
        indexs = range(0, len(df))
        print 'df length:{}'.format(len(indexs))
        df.index = indexs
        if len(df) == 0:
            continue

        df['keys'] = ''
        df['tags'] = ''
        print df

        pool = ThreadPool(processes=10)
        pool.map(_get_one_article_keys, indexs)
        pool.close()
        pool.join()

        keys_list = []
        tag_list = []
        for ix, row in df.iterrows():
            print row['keys']
            #keys_list.extend(row['keys'].strip().split(','))
            tag_list.extend(row['tags'].strip().split(','))

        # print len(keys_list)
        # fdist = FreqDist(keys_list)
        # print len(fdist.keys())
        # f = file('fdist_{}.pkl'.format(i), 'wb')
        # pickle.dump(fdist, f)
        # f.close()

        fdist_tag = FreqDist(tag_list)
        print len(fdist_tag.keys())
        f = file('ftags_{}.pkl'.format(i), 'wb')
        pickle.dump(fdist_tag, f)
        f.close()

def test_fenci():

    for i in range(2, 9):
        f = file('ftags_{}.pkl'.format(i), 'rb')
        fdist = pickle.load(f)
        fdist.plot(50)
        keys = fdist.keys()[:50]
        print keys
    f.close()

if __name__ == "__main__":
    print 'begin'
    # test_sent = (
    #     "李小福是创新办主任也是云计算方面的专家; 什么是八一双鹿\n"
    #     "例如我输入一个带“韩玉赏鉴”的标题，在自定义词库中也增加了此词为N类\n"
    #     "「台中」正確應該不會被切開。mac上可分出「石墨烯」；此時又可以分出來凱特琳了。"
    #     )
    # words = jieba.cut(test_sent)
    # print('/'.join(words))
    test_sina_finance()
    #test_fenci()

    #f = open('../Data/weixin.md')
    #fenci(f.read())