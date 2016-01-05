#coding=utf8

__author__ = 'cbb'

import feedparser
import re

def get_word_counts(url):
    """
    返回一个RSS订阅源的标题和包含单词计数情况的字典
    :param url:
    :return:
    """

    #解析订阅源
    d = feedparser.parse(url)
    wc = {}

    #循环遍历所有的文章条目
    for e in d.entries:
        if 'summary' in e:
            summary = e.summary
        else:
            summary = e.description

        #提取一个单词列表
        words = get_words(e.title + ' ' + summary)
        for word in words:
            wc.setdefault(word, 0)
            wc[word] += 1

    return d.feed.title, wc

def get_words(html):
    #去除所有HTML标记
    txt = re.compile(r'<[^>]+>').sub('', html)

    #利用所有非字母字符拆分单词
    words = re.compile(r'[^A-Z^a-z]+').split(txt)

    #转化成小写形式
    return [word.lower() for word in words if word !='']

get_word_counts('http://news.baidu.com/n?cmd=1&class=stock&tn=rss')