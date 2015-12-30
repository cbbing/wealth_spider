# -*- coding:utf8 -*-

# -*- coding:utf8 -*-

import ConfigParser
import requests
import pickle
import cookielib
import re
import time
import random
import pandas as pd
from pandas import DataFrame
from bs4 import BeautifulSoup as bs

from util.webHelper import get_web_driver, get_requests
from util.CodeConvert import regularization_time, encode_wrap
from db_config import mysql_table_licaishi_viewpoint, engine

class Licaishi:

    def __init__(self):
        self.site = 'http://licaishi.sina.com.cn'
        self.url = self.site + '/planner/{user_id}/4?page={pid}'
        self.max_page_count = 10

        self.dir_temp = './Data/Temp/'



    def get_new_driver(self):
        url_login = 'http://login.weibo.cn/login/'
        driver = get_web_driver(url_login, has_proxy=False)
        #driver.save_screenshot('../Data/weibo.png')
        driver.find_element_by_xpath('//input[@type="text"]').send_keys('cbb6150')
        driver.find_element_by_xpath('//input[@type="password"]').send_keys('xx.785906')

        driver.find_element_by_xpath('//input[@type="submit"]').click()

        # 获得 cookie信息
        cookie = driver.get_cookies()

        print cookie
        print len(cookie)
        # dict_cookie = cookie[-1]
        #
        # data_cookie = ''
        # for key in dict_cookie.keys():
        #     data_cookie += "{}={};".format(key, dict_cookie[key])

        f = open(self.dir_temp + 'cookie','w')
        pickle.dump(cookie, f)

        return driver

        #driver.quit()
        #return data_cookie


    def get_licaishi_viewpoint_list(self, user_id):
        """
        理财师观点
        :param user_id:
        :return:
        """

        url = self.url.format(user_id=user_id, pid=1)
        r = get_requests(url, has_proxy=False)
        #print r.text

        soup = bs(r.text, 'lxml')

        # 获取关注的总页码
        page_count = self._get_page_count(soup)

        # 获取数据库中的最新发表文章时间
        publish_time_lastest = self._get_lastest_publish_time(mysql_table_licaishi_viewpoint, user_id)

        current_page = 1
        while(current_page < min((page_count+1), self.max_page_count+1)):
            print "Page:%d / %d" % (current_page, page_count)
            article_list_one_page = self._get_licaishi_viewpoint_list_in_one_page(soup, user_id)

            # 存入mysql
            [archive.to_mysql() for archive in article_list_one_page] #不需判断数据库是否存在,若存在则抛出异常,不插入

            # 判断是否存在最新文章
            if len(article_list_one_page) > 0:
                archive = article_list_one_page[-1]
                if archive.publish_time < str(publish_time_lastest):

                    print encode_wrap('{}:已经获取到最新的微博了'.format(user_id))
                    break

            current_page += 1
            wait_time = self._get_wait_time()
            time.sleep(wait_time)
            print 'Page:{}   Wait time:{}'.format(current_page, wait_time)

            # 点击下一页
            url = self.url.format(user_id=user_id, pid=current_page)
            r = get_requests(url, has_proxy=False)
            soup = bs(r.text, 'lxml')


        #return article_list

    def get_weibo_by_api(self):
        pass

    ### 类中的辅助函数
    def _get_page_count(self, soup):
        """
        获取总页码
        :param soup:
        :return page_count:
        """

        try:

            pagerUL = soup.find('div', {'class':'s_widget w_pages'})
            data_pages = pagerUL.find('a', {'class':'w_pages_next'})
            page_count = 0
            if data_pages:
                page_count = int(data_pages['data-page'])
        except Exception,e:
            # 只有一页
            page_count = 1
        return page_count

    # 获取一页中的观点列表
    def _get_licaishi_viewpoint_list_in_one_page(self, soup, user_id):

        archiveList = []

        try:

            statusAll = soup.find('div', {'class':'s_left'})
            statusList = statusAll.findAll('div', {'class':'s_widget w_vp'})
            for status in statusList:

                try:

                    archive = Article()
                    archive.user_id = user_id

                    h2_title = status.find('h2', {'class':'w_vp_h2'})
                    if h2_title:
                        archive.title = h2_title.get_text().strip()
                        a_href = h2_title.find('a')
                        if a_href:
                            archive.href = self.site + a_href['href']

                    p_detail = status.find('p', {'class':'w_vp_p'})
                    if p_detail:
                        archive.detail = p_detail.get_text().strip()

                    div_time = status.find('span', {'class':'w_vp_de'})
                    if div_time:
                        archive.publish_time = regularization_time(div_time.get_text().strip())

                    a_device = status.find('a', {'class':'w_vp_fra'})
                    if a_device:
                        archive.device = a_device.get_text().strip()

                    div_watch_count = status.find('div', {'class':'w_vp_ort'})
                    if div_watch_count:
                        watch_count = div_watch_count.get_text().strip().replace('人阅读','')
                        archive.watch_count = int(watch_count)

                    archiveList.append(archive)

                except Exception, e:
                    print e
        except Exception, e:
                print e

        return archiveList

    # 获取等待时间(随机)
    def _get_wait_time(self):
        cf = ConfigParser.ConfigParser()
        cf.read('./config.ini')

        wait_time = int(cf.get('web', 'wait_time'))  # second
        wait_time_random = random.randint(wait_time, wait_time*2)
        return wait_time_random

    def _click_next_page(self, driver):
        try:
            driver.find_element_by_link_text('下页').click()
            return True
        except Exception,e:
            print e
            return False

    def _get_lastest_publish_time(self, table, user_id):
        """
        获取数据库中的最新发表文章时间
        :param table:
        :param user_id:
        :return:
        """

        publish_time_lastest = '2000-01-01 00:00:00'
        try:
            sql = "select max(publish_time) as publish_time from {0} where user_id='{1}'".format(table, user_id)
            df = pd.read_sql_query(sql, engine)
            if len(df) > 0 and not df.ix[0, 'publish_time'] is None:
                publish_time_lastest = df.ix[0, 'publish_time']

                print str(publish_time_lastest)
        except Exception,e:
            print e

        return publish_time_lastest


# 微博文章
class Article:
    def __init__(self):
        self.user_id = ''
        self.title = ''
        self.detail = ''
        self.publish_time = ''
        self.device = ''
        self.href = ''
        self.watch_count = 0   #阅读量
        self.repost_count = 0  # 转发数
        self.donate_count = 0  # 赞助数
        self.comment_count = 0 # 评论数
        # self.is_top = False       # 是否置顶
        # self.is_repost = False    # 是否转发
        # self.repost_reason = ''    # 转发理由

    def to_mysql(self):

        try:

            df = DataFrame({'user_id':[self.user_id],
                            'title':[self.title],
                            'detail': [self.detail],
                            'publish_time':[self.publish_time],
                            'href':[self.href],
                            'watch_count':[self.watch_count],
                            'repost_count':[self.repost_count],
                            'donate_count':[self.donate_count],
                            'comment_count':[self.comment_count],
                            #'is_top':[self.is_top],
                            #'is_repost':[self.is_repost],
                            #'repost_reason':[self.repost_reason
                            'device':[self.device],# ]

                            },
                           columns=['user_id', 'title', 'detail',
                                    'publish_time', 'href','watch_count',
                                    'repost_count', 'donate_count',
                                    'comment_count', 'device'])
            print df

            try:
                sql_del = "delete from {table} where user_id='{user_id}' and title='{title}' and publish_time='{publish_time}'".format(
                        table = mysql_table_licaishi_viewpoint,
                        user_id = self.user_id,
                        title = self.title,
                        publish_time = self.publish_time
                        )
                engine.execute(sql_del)
            except Exception,e:
                print 'delete error!  table:{} not exist!'.format(mysql_table_licaishi_viewpoint)

            df.to_sql(mysql_table_licaishi_viewpoint, engine, if_exists='append', index=False)
            return True

        except Exception,e:
            print e
            return False

if __name__ == "__main__":
    licaishi = Licaishi()
    #weibo.get_cookie()
    licaishi.get_licaishi_viewpoint_list('2357529875')