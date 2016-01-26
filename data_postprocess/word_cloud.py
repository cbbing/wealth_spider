#coding=utf8

# File: ex4.py
# Date: 05/14/13
# Author: Simon Roses Femerling
# Desc: Create word cloud
#
# VULNEX (C) 2013
# www.vulnex.com
# http://python.jobbole.com/84197/

import requests
import json
import urllib
import pickle

from pytagcloud import create_tag_image, make_tags
from pytagcloud.lang.counter import get_tag_counts

#文件名: ch.py
def set_ch():
    from pylab import mpl
    mpl.rcParams['font.sans-serif'] = ['SimHei']#['FangSong'] # 指定默认字体
    mpl.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题

#set_ch()

def keys_cloud():
	for i in range(9):
		f = file('../data_preprocess/Data/ftags_{}.pkl'.format(i), 'rb')
		fdist = pickle.load(f)
		tag = ''
		print fdist.most_common()[0][0], fdist.most_common()[0][1]
		for key, count in fdist.most_common(100):
			tag +=( key+" ")*count

		#text = "%s" % " ".join(tag)
		#tags = make_tags(get_tag_counts('cbb cbb xuxian xuxian keke keke keke'),maxsize=100)
		tags = make_tags(get_tag_counts(tag),maxsize=100)
		# Set your output filename
		create_tag_image(tags,"Data/word_cloud_{}.png".format(i), size=(600,400),background=(0, 0, 0, 255), fontname="SimHei")

keys_cloud()
#site="http://search.twitter.com/search.json?q="

# Your query here
# query=""
#
# url=site+urllib.quote(query)
#
# response = requests.get(url)
#
# tag = []
# for res in response.json["results"]:
# 	tag.append(res["text"].encode('ascii','ignore'))
#
# text = "%s" % "".join(tag)
# tags = make_tags(get_tag_counts(text),maxsize=100)
# # Set your output filename
# create_tag_image(tags,"antpji_word_cloud.png", size=(600,500), fontname="Lobster")

# VULNEX EOF