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
from util.helper import fn_timer

engine_sqlite = create_engine('sqlite:///foo.db')

@fn_timer
def train_classifier():
    df = pd.read_sql("select classify, tags, title, content from {}".format(mysql_table_sina_finance+"200000"), engine_sqlite)
    values = df.get_values()
    #featuresets = [(key_features(tag), classify) for classify, tag, _, _ in values]
    #train_set, test_set = featuresets[:180000], featuresets[180000:]

    train_set, test_set = [], []

    filename = 'Data/classifier.pkl'
    if not os.path.exists(filename):
        classifier = nltk.NaiveBayesClassifier.train(train_set)

        with open(filename, 'wb') as f:
            cPickle.dump(classifier, f)
    else:
        with open(filename, 'rb') as f:
            classifier = cPickle.load(f)

    #print nltk.classify.accuracy(classifier, test_set)
    errors = []

    # for classify, tag in test_set:
    #     guess = classifier.classify(key_features(tag))
    #     if guess != classify:
    #         errors.append((classify, guess,tag))
    # df = pd.DataFrame(errors, columns=[u'类别',u'预测',u'标签'])
    print 'test_len',len(values[180000:])
    for (classify, tag, title, _) in values[180000:]:
        guess = classifier.classify(key_features(tag))
        if guess != classify:
            errors.append((classify, guess, title, tag))

    print 'error_len',len(errors)
    df = pd.DataFrame(errors, columns=[u'类别',u'预测',u'标题',u'标签'])
    df.to_csv('Data/errors.csv')
    with pd.ExcelWriter('Data/errors.xlsx') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=True)

    # for (classify, guess, title) in errors:
    #     print 'correct={:>8} guess={:>8} title={:>30}'.format(classify, guess, title)

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
        #df = cPickle.load(file('Data/df_all.pkl', 'rb'))
        df = pd.read_sql("select * from {} limit 200000".format(mysql_table_sina_finance), engine)
        #df = pd.read_sql_table(mysql_table_sina_finance, engine)
        print 'before len:{}'.format(len(df))
        df = df[df['content'].apply(lambda x : (not x is None and len(x)) > 0)]
        print 'after len:{}'.format(len(df))
        df.drop_duplicates(inplace=True)
        print 'after len:{}'.format(len(df))

        df.to_sql(mysql_table_sina_finance, engine_sqlite, if_exists='replace')

    print df.head()
    df.sort_index(by='time', ascending=True, inplace=True)

    df = df[:200000]
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

    df.to_sql(mysql_table_sina_finance+"200000", engine_sqlite, if_exists='replace')



if __name__ == "__main__":
    #data_preprocess()
    train_classifier()