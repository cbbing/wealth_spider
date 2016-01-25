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

def keys_cloud():
	f = file('../data_preprocess/Data/ftags_0.pkl', 'rb')
	fdist = pickle.load(f)
	for item in fdist.item():
		print item
		#content = item *

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