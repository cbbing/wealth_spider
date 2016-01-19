#coding=utf8

# 分词

import re
import jieba
jieba.load_userdict('../Data/userdict.txt')
import jieba.analyse
from nltk import FreqDist

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

def test_sina_finance():
    import pandas as pd
    from db_config import engine, mysql_table_sina_finance
    classifies = ['美股', '国内财经', '证券', '国际财经', '生活', '期货', '外汇', '港股', '产经', '基金']
    sql = "select title, content from {table} where classify='{classify}'".format(table=mysql_table_sina_finance, classify=classifies[1])
    df = pd.read_sql(sql, engine)
    print df
    for ix, row in df.iterrows():
        content = row['title'] + " " + row['content']
        seg_list = jieba.cut(content)


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

    f = open('../Data/weixin.md')
    fenci(f.read())