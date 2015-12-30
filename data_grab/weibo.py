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
from db_config import mysql_table_weibo_article, engine

class Weibo:

    def __init__(self):
        self.url = 'http://weibo.cn/{user_id}'
        self.max_page_count = 20

        self.dir_temp = './Data/Temp/'



    def get_new_driver(self):
        url_login = 'http://login.weibo.cn/login/'
        driver = get_web_driver(url_login, has_proxy=False)
        #driver.save_screenshot('../Data/weibo.png')
        driver.find_element_by_xpath('//input[@type="text"]').send_keys('cbb6150')
        driver.find_element_by_xpath('//input[@type="password"]').send_keys('12356789')

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

    def get_login_request(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
        data={'mobile':'15910361722', 'password_9075':'12356789', 'remember':'on','backURL':'http://www.weibo.cn','backTitle':'手机新浪网','vk':'9075_fcd6_2358975340'}
        url = 'http://login.weibo.cn/login/'
        r = requests.post(url, data = data, headers=headers)


    def get_weibo_list(self, user_id):

        # try:
        #     f = open(self.dir_temp + 'cookie','r')
        #     data_cookie = pickle.load(f)
        # except Exception,e:
        #     self.get_new_cookie()
        #     f = open(self.dir_temp + 'cookie','r')
        #     data_cookie = pickle.load(f)
        #
        # cookdic = dict(Cookie=data_cookie)
        #
        # url = self.url.format(user_id=user_id)
        # r = get_requests(url, has_proxy=True, cookie=cookdic)

        driver = self.get_new_driver()

        url = self.url.format(user_id=user_id)
        driver.get(url)

        soup = bs(driver.page_source, 'lxml')

        # 获取关注的总页码
        page_count = self._get_page_count(soup)

        # 获取数据库中的最新发表文章时间
        publish_time_lastest = self._get_lastest_publish_time(mysql_table_weibo_article, user_id)

        current_page = 1
        while(current_page < min((page_count+1), self.max_page_count+1)):
            print "Page:%d / %d" % (current_page, page_count)
            article_list_one_page = self._get_weibo_user_list_in_one_page(soup, user_id)

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
            driver.find_element_by_link_text('下页').click()

            clickStatus = self._click_next_page(driver)
            if clickStatus:
                soup = bs(driver.page_source, 'lxml')

            else:
                print encode_wrap('无下一页{0}, 退出...'.format(current_page))
                break

        #return article_list
        driver.quit()

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

            pagerUL = soup.find('div', {'class':'pa'})
            data_pages = pagerUL.find('input', {'name':'mp', 'type':'hidden'})
            page_count = 0
            if data_pages:
                page_count = int(data_pages['value'])
        except Exception,e:
            # 只有一页
            page_count = 1
        return page_count

    # 获取一页中的粉丝/关注列表
    def _get_weibo_user_list_in_one_page(self, soup, user_id):

        archiveList = []

        try:

            #statusAll = soup.find('div', {'class':'c'})
            statusList = soup.findAll('div', {'class':'c'})
            for status in statusList:

                try:

                    archive = Article()
                    archive.user_id = user_id

                    archive.detail = status.find('span', {'class':'ctt'}).get_text()

                    # 发布时间, 设备
                    timeAndDevice = status.find('span', {'class':'ct'}).get_text()
                    timeAndDevice = timeAndDevice.split('来自')
                    if len(timeAndDevice) == 2:
                        archive.publish_time = regularization_time(timeAndDevice[0].strip())
                        archive.device = timeAndDevice[1].strip()

                    infos = status.find_all('div')
                    if len(infos) >= 2:
                        info = infos[-1].get_text()
                        m = re.search(u'赞\[(\d+)\]', info)
                        if m:
                            archive.donate_count = m.group(1)

                        m = re.search(u'转发\[(\d+)\]', info)
                        if m:
                            archive.repost_count = m.group(1)

                        m = re.search(u'评论\[(\d+)\]', info)
                        if m:
                            archive.comment_count = m.group(1)

                        # 是否为转发
                        if '转发理由:' in info:
                            m = re.search(u'转发理由:(.*)赞', info)
                            if m:
                                archive.is_repost = True
                                archive.repost_reason = m.group(1)

                    try:
                        # 置顶
                        spanKt = status.find('span', {'class':'kt'})
                        if spanKt and '置顶' in spanKt.get_text():
                            archive.is_top = True

                    except:
                        print 'arctive is no top'

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
        # self.title = ''
        self.detail = ''
        self.publish_time = ''
        self.device = ''
        # self.href = ''
        self.repost_count = 0  # 转发数
        self.donate_count = 0  # 赞助数
        self.comment_count = 0 # 评论数
        self.is_top = False       # 是否置顶
        self.is_repost = False    # 是否转发
        self.repost_reason = ''    # 转发理由

    def to_mysql(self):

        try:

            df = DataFrame({'user_id':[self.user_id],
                            #'title':[self.title],
                            'detail': [self.detail],
                            'publish_time':[self.publish_time],
                            'device':[self.device],
                            #'href':[self.href],
                            'repost_count':[self.repost_count],
                            'donate_count':[self.donate_count],
                            'comment_count':[self.comment_count],
                            'is_top':[self.is_top],
                            'is_repost':[self.is_repost],
                            'repost_reason':[self.repost_reason]

                            },
                           columns=['user_id', 'detail',
                                    'publish_time', 'repost_count', 'donate_count',
                                    'comment_count', 'repost_reason', 'is_repost', 'is_top', 'device'])
            print df

            sql_del = "delete from {table} where user_id='{user_id}' and detail='{detail}' and publish_time='{publish_time}'".format(
                    table = mysql_table_weibo_article,
                    user_id = self.user_id,
                    detail = self.detail,
                    publish_time = self.publish_time
                    )
            engine.execute(sql_del)

            df.to_sql(mysql_table_weibo_article, engine, if_exists='append', index=False)
            return True

        except Exception,e:
            print e
            return False

if __name__ == "__main__":
    weibo = Weibo()
    #weibo.get_cookie()
    weibo.get_weibo_list('2144596567')