#coding=utf8
"""
    分类器
"""
import os
import cPickle
import pandas as pd
import multiprocessing
import time
from sqlalchemy import create_engine
import nltk

from db_config import engine, mysql_table_sina_finance
from data_preprocess.fenci import get_one_article_keys

engine_sqlite = create_engine('sqlite:///foo.db')

def train_classifier():
    df = pd.read_sql("select classify, tags from {}".format(mysql_table_sina_finance+"50000"), engine_sqlite)
    values = df.get_values()
    featuresets = [(key_features(tag), classify) for classify, tag in values]
    train_set, test_set = featuresets[:900], featuresets[900:]
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    print nltk.classify.accuracy(classifier, test_set)


def key_features(tags_content):
    tags = tags_content.split(',')
    tags = tags[:30]
    tag_dict = {}
    for i in range(len(tags)):
        tag_dict['tag_{}'.format(i)] = tags[i]

    return tag_dict

def data_preprocess():
    try:
        df = pd.read_sql("select * from {}".format(mysql_table_sina_finance), engine_sqlite)
    except Exception,e:
        print e
        df = pd.DataFrame()
    if len(df)== 0:
        df = cPickle.load(file('Data/df_all.pkl', 'rb'))
        #df = pd.read_sql_table(mysql_table_sina_finance, engine)
        print 'before len:{}'.format(len(df))
        df = df[df['content'].apply(lambda x : (not x is None and len(x)) > 0)]
        print 'after len:{}'.format(len(df))
        df.drop_duplicates(inplace=True)
        print 'after len:{}'.format(len(df))

        df.to_sql(mysql_table_sina_finance, engine_sqlite, if_exists='replace')

    print df.head()
    df.sort_index(by='time', ascending=True, inplace=True)

    df = df[:50000]
    print df.head()

    t0 = time.time()
    pool = multiprocessing.Pool(processes = 4)
    contents = []
    for ix, row in df.iterrows():
        content = ''
        try:
            content = row['title']
            if row['content']:
                content += " " + row['content']
        except Exception,e:
            print e
        finally:
            contents.append(content)

    results = pool.map(get_one_article_keys, contents)
    pool.close()
    pool.join()
    t1 = time.time()
    print 'time pass:{:.3f}'.format(t1-t0)
    df['tags'] = results

    df.to_sql(mysql_table_sina_finance+"50000", engine_sqlite, if_exists='replace')



if __name__ == "__main__":
    data_preprocess()
    train_classifier()