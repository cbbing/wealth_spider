# -*- coding:utf8 -*-

import time
import random

import util.webHelper as wh
import util.codeConvert as cc
import util.html2text as html2text

from bs4 import BeautifulSoup as bs
from pandas import DataFrame
from selenium import webdriver

from db_config import mysql_table_weixin_article, engine

class Weixin:

    def __init__(self):
        self.site = 'http://weixin.sogou.com'
        self.url = self.site + '/gzh?openid=oIWsFtyFo9hdOX4Qk61z6m2ZUfM4&ext=4egMG4BCzZ86knUuhl74BPovYnb4rRvGnihcvfHgBsMGXrnOtOgRkDlCK81QA3VL'

    def get_article_list(self):
        urls = self._get_lastest_weixin_urls()
        for weixin_id, weixin_name, url in urls:
            self.get_one_weixin_gzh(weixin_id, weixin_name, url)

    # 获取一个公众号的文章列表
    def get_one_weixin_gzh(self, weixin_id, weixin_name, url):

        def _get_articl_detail(driver, article):

            driver.get(article.href)
            article.href = driver.current_url

            soup = bs(driver.page_source, 'lxml')
            detail_div = soup.find('div', {'class':'rich_media_content '})
            # article.detail = detail_div.get_text()
            if detail_div:
                md = html2text.html2text(detail_div.prettify())
                article.detail = md

            stop = 3 * (1 + random.random())
            time.sleep(stop)
            print article.href
            print 'sleep:{:.2f}s\n'.format(stop)

        driver = wh.get_web_driver(url)

        # 点击"查看更多",非登录用户最多显示100篇,点击10次
        try:
            for _ in range(0,1):
                driver.find_element_by_link_text('查看更多').click()
                time.sleep(3)
        except:
            None

        soup = bs(driver.page_source, 'lxml')

        article_list = []

        wxBox = soup.find('div', {'id':'wxbox'})
        txtBoxs = wxBox.find_all('div', 'txt-box')
        for box in txtBoxs:
            a = box.find('a')
            if not a:
                continue

            article = Article()
            article.title = a.get_text()

            article.user_id = weixin_id
            article.user_name = weixin_name

            article.href = self.site + a['href']


            s_p = box.find('div', {'class':'s-p'})
            if s_p:
                article.publish_time = cc.GetTime2(int(s_p['t']))
            print article.user_name
            article_list.append(article)

        for article in article_list:
            _get_articl_detail(driver, article)
            article.to_mysql()

        driver.quit()

    def _get_lastest_weixin_urls(self):

        urls = []

        url_search = 'http://weixin.sogou.com/weixin?type=1&query={key}&ie=utf8'
        f = open('../Data/weixin_gzh.txt')
        for line in f.readlines():
            weixin_id, weixin_name, openid = line.split(',')
            weixin_id = weixin_id.strip()
            weixin_name = weixin_name.strip()
            openid = openid.strip()

            r = wh.get_requests(url_search.format(key=weixin_id), has_proxy=False)
            soup = bs(r.text)
            div_all = soup.find_all('div', {'class':'wx-rb bg-blue wx-rb_v1 _item'})
            for div in div_all:
                href = div['href']
                if openid in href:
                    urls.append((weixin_id, weixin_name, self.site + href))
                    break

        return urls







# 微博文章
class Article:
    def __init__(self):
        self.user_id = ''
        self.user_name = ''
        self.title = ''
        self.detail = ''
        self.publish_time = cc.GetNowTime()
        self.capture_time = '' # 抓取时间
        self.device = ''
        self.href = ''
        # self.repost_count = 0  # 转发数
        # self.donate_count = 0  # 赞助数
        # self.comment_count = 0 # 评论数
        # self.is_top = False       # 是否置顶
        # self.is_repost = False    # 是否转发
        # self.repost_reason = ''    # 转发理由

    def to_mysql(self):

        try:

            df = DataFrame({'user_id':[self.user_id],
                            'user_name':[self.user_name],
                            'title':[self.title],
                            'detail': [self.detail],
                            'publish_time':[self.publish_time],
                            'capture_time':[self.capture_time],
                            'device':[self.device],
                            'href':[self.href],
                            # 'repost_count':[self.repost_count],
                            # 'donate_count':[self.donate_count],
                            # 'comment_count':[self.comment_count],
                            # 'is_top':[self.is_top],
                            # 'is_repost':[self.is_repost],
                            # 'repost_reason':[self.repost_reason]

                            },
                           columns=['user_id', 'user_name', 'title', 'detail',
                                    'publish_time', 'capture_time', 'device','href'])
            print df

            try:
                sql_del = "delete from {table} where user_id='{user_id}' and href='{href}' and publish_time='{publish_time}'".format(
                        table = mysql_table_weixin_article,
                        user_id = self.user_id,
                        href = self.href,
                        publish_time = self.publish_time
                        )
                engine.execute(sql_del)
            except Exception,e:
                print 'delete error!', str(e)

            df.to_sql(mysql_table_weixin_article, engine, if_exists='append', index=False)
            return True

        except Exception,e:
            print e
            return False

if __name__ == '__main__':
    weixin = Weixin()
    weixin.get_article_list()