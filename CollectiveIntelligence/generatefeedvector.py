#coding=utf8

import sys
reload(sys)
sys.setdefaultencoding('utf8')

__author__ = 'cbb'

import feedparser
import re
import jieba

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

    txt = re.compile('\s').sub('', txt)

    #利用所有非字母字符拆分单词
    #words = re.compile(r'[^A-Z^a-z]+').split(txt) #英文分词
    words = jieba.cut(txt)


    #转化成小写形式
    return [word for word in words if word !='']

# news = get_word_counts('http://news.baidu.com/n?cmd=1&class=stock&tn=rss')
# print news[0], news[1]


apcount = {}
wordcounts = {}
feedlist = [line for line in file('../Data/feedbaidu.txt', 'r')]
for feedurl in feedlist:
    title, wc = get_word_counts(feedurl.strip())
    wordcounts[title] = wc
    for word, count in wc.items():
        apcount.setdefault(word, 0)
        if count > 1:
            apcount[word] += 1

wordlist = []
for w, bc in apcount.items():
    frac = float(bc)/len(feedlist)
    if frac > 0.1 and frac < 0.5:
        wordlist.append(w)

out = file('blogdata.txt', 'w')
out.write('Blog')
for word in wordlist:
    out.write('\t{}'.format(word))
out.write('\n')
for blog, wc in wordcounts.items():
    out.write(blog)
    for word in wordlist:
        if word in wc:
            out.write('\t{}'.format(wc[word]))
        else:
            out.write('\t0')
    out.write('\n')
out.close()























