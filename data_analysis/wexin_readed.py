#coding: utf-8

"""
微信阅读量
"""

from selenium import webdriver
import time
from bs4 import BeautifulSoup as bs
from util.codeConvert import GetNowTime

for i in range(1000):
    dr = webdriver.PhantomJS()
    url='http://mp.weixin.qq.com/s?__biz=MzI0MTQxMzEwNA==&mid=2247483683&idx=1&sn=4b6e6785ae9588249715e0ffb31b19a9&scene=1&srcid=0615SliT4YQWkITEygD0oDJ6&from=singlemessage&isappinstalled=0#wechat_redirect'
    dr.get(url)
    # time.sleep(3)
    soup = bs(dr.page_source, 'lxml')
    title =  soup.find('h2', {'class':"rich_media_title"})
    print GetNowTime(), '{}/{}'.format(i+1, 1000)
    print title.text


    dr.quit()