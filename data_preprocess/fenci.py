#coding=utf8

# 分词

import re
import jieba
jieba.load_userdict('../Data/userdict.txt')
import jieba.analyse

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

    @fn_timer
    def get_dataframe():
        import pandas as pd
        from db_config import engine, mysql_table_sina_finance
        classifies = ['美股', '国内财经', '证券', '国际财经', '生活', '期货', '外汇', '港股', '产经', '基金']
        sql = "select title, content from {table} where classify='{classify}'".format(table=mysql_table_sina_finance, classify=classifies[1])
        df = pd.read_sql(sql, engine)
        return df

    df = get_dataframe()

    indexs = range(0, len(df))
    len_df = len(df)
    print 'items:{}'.format(len(indexs))

    f = open('../Data/stopwords.txt','r')
    stopwords = f.read().split('\n')

    keys_list = []

    #创建锁
    mutex = threading.Lock()

    @threads(10)
    def _get_one_article_keys(row):
        try:
            content = row['title'] + " " + row['content']
            seg_list = jieba.cut(content)
            keys_each = [seg for seg in seg_list if seg not in stopwords]

            if mutex.acquire(): #锁定
                keys_list.extend(keys_each)
                mutex.release()
        except Exception,e:
            print e

    [_get_one_article_keys(row) for ix, row in df.iterrows()]

    # for ix, row in tqdm(df.iterrows()):
    #     try:
    #         content = row['title'] + " " + row['content']
    #         seg_list = jieba.cut(content)
    #         keys_each = [seg for seg in seg_list]
    #         keys_list.extend(keys_each)
    #     except Exception,e:
    #         print e



    # def _cut_each(ix):
    #     try:
    #         row = df.ix[ix]
    #         content = row['title'] + " " + row['content']
    #         seg_list = jieba.cut(content)
    #         keys_each = [seg for seg in seg_list]
    #         keys_list.extend(keys_each)
    #         #print 'keys_list length:{}'.format(len(keys_list))
    #         print 'index:{}/{}'.format(ix, len_df)
    #     except Exception, e:
    #         print 'index:', ix, e
    #
    #
    # pool = ThreadPool(processes=20)
    # pool.map(_cut_each, indexs)
    # pool.close()
    # pool.join()

    fdist = FreqDist(keys_list)

    print len(fdist.keys())
    f = file('fdist.pkl', 'wb')
    pickle.dump(fdist, f)
    f.close()

def test_fenci():

    f = open('../Data/stopwords.txt','r')
    stopwords = f.read().split('\n')

    f = file('keys_list.pkl', 'rb')
    seg_list = pickle.load(f)
    fdist = FreqDist([seg for seg in seg_list if seg not in stopwords])
    fdist.plot(50)

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

    f = open('../Data/weixin.md')
    #fenci(f.read())