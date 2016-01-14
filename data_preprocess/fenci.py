#coding=utf8

# 分词

import jieba
from nltk import FreqDist

def fenci(data):
    seg_list = jieba.cut(data)

    fdist = FreqDist([seg for seg in seg_list])
    fdist.plot(50)
