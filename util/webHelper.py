#!/usr/local/bin/python
#coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import requests
import random
import ConfigParser
import pickle
import pandas as pd

from retrying import retry
from selenium import webdriver
from selenium.webdriver.common.proxy import *

from CodeConvert import encode_wrap, GetNowDate
from db_config import engine

# 浏览器的窗口最大化
def max_window(driver, width_scale=1, height_scale=2):
    driver.maximize_window()
    siz = driver.get_window_size()
    driver.set_window_size(siz['width']*width_scale, siz['height']*height_scale)


@retry(stop_max_attempt_number=100)
def get_requests(url, has_proxy=True, cookie=None):
    """
    requests使用代理请求
    :param url:
    :param ip_dataframe:
    :return requests:
    """

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}

    proxy = None
    if has_proxy:
        proxy = get_proxies()
    cf = ConfigParser.ConfigParser()
    cf.read('../config.ini')
    timeout = int(cf.get('web', 'timeout'))

    r = requests.get(url, proxies=proxy, headers=headers, cookies=cookie,timeout=timeout)
    output = 'Code:{1}  Proxy:{2}  Url:{0}  '.format(url, r.status_code, proxy)
    print encode_wrap(output)

    if int(r.status_code) != 200:
        raise Exception('request fail')

    return r


@retry(stop_max_attempt_number=100)
def get_web_driver(url, has_proxy=True):
    """
    Selenium 使用代理请求
    :param url:
    :return driver:
    """

    if has_proxy:
        proxies = get_proxies()
        if proxies.has_key('http'):
            myProxy = proxies['http']
        elif proxies.has_key('https'):
            myProxy = proxies['https']

        proxy = Proxy({
           'proxyType': ProxyType.MANUAL,
            'httpProxy': myProxy,
            # 'ftpProxy': myProxy,
            # 'sslProxy': myProxy,
            # 'noProxy':d ''
        })
        print encode_wrap("使用代理:"), myProxy
        driver = webdriver.Firefox(proxy=proxy)
    else:
        driver = webdriver.Firefox()

    #driver.set_page_load_timeout(30)
    driver.get(url)

    return driver

# 获取IP代理地址(随机)
def get_proxies():

    file_name = './Data/Temp/ip_data_tmp_{}'.format(GetNowDate())
    try:
        mydb = open(file_name, 'r')
        df_ip = pickle.load(mydb)
        if not type(df_ip) is pd.DataFrame:
            raise IOError('file error')

    except Exception,e:
        print e
        mysql_table_ip = 'ip_proxy'
        sql = 'select * from {0} where Speed > 0 order by Speed limit {1}'.format(mysql_table_ip, 1000)
        df_ip = pd.read_sql_query(sql, engine)
        mydb = open(file_name, 'w')
        pickle.dump(df_ip, mydb)

    if len(df_ip) > 0:

        index = random.randint(0, len(df_ip))
        print 'IP proxy length:{0}, Random Index:{1}'.format(len(df_ip), index)
        http = df_ip.ix[index, 'Type']
        http = str(http).lower()
        ip = df_ip.ix[index, 'IP']
        port = df_ip.ix[index, 'Port']
        ip_proxy = "%s://%s:%s" % (http, ip, port)
        proxies = {http:ip_proxy}
        return proxies
    else:
        return {}