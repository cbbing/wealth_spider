# -*- coding:utf8 -*-

import ConfigParser
import requests
import pickle
import cookielib, urllib2,urllib
from bs4 import BeautifulSoup as bs


from util.webHelper import get_web_driver, get_requests

class Weibo:

    def __init__(self):
        self.url = 'http://weibo.cn/{user_id}'

    def get_new_cookie(self):
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
        dict_cookie = cookie[-1]

        data_cookie = ''
        for key in dict_cookie.keys():
            data_cookie += "{}={};".format(key, dict_cookie[key])

        f = open('cookie','w')
        pickle.dump(data_cookie, f)

        driver.quit()
        return data_cookie


    def get_weibo_list(self, user_id):

        try:
            f = open('cookie','r')
            data_cookie = pickle.load(f)
        except Exception,e:
            data_cookie = self.get_new_cookie()

        cookdic = dict(Cookie=data_cookie)

        url = self.url.format(user_id=user_id)
        r = get_requests(url, has_proxy=True, cookie=cookdic)

        soup = bs(r.text, 'html5lib')
        self._get_page_count(soup)
        print r.text
        # driver = get_web_driver(url, has_proxy=False)
        # print driver.page_source

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
                page_count = data_pages['value']
        except Exception,e:
            # 只有一页
            page_count = 1
        return page_count


if __name__ == "__main__":
    weibo = Weibo()
    #weibo.get_cookie()
    weibo.get_weibo_list('2144596567')