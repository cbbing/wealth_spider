#!/usr/local/bin/python
#coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import requests
import random
import ConfigParser

from retrying import retry

from CodeConvert import encode_wrap

# 浏览器的窗口最大化
def max_window(driver, width_scale=1, height_scale=2):
    driver.maximize_window()
    siz = driver.get_window_size()
    driver.set_window_size(siz['width']*width_scale, siz['height']*height_scale)


# requests使用代理请求
@retry(stop_max_attempt_number=100)
def get_requests(url, ip_dataframe):

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}

    proxy = get_proxies(ip_dataframe)
    cf = ConfigParser.ConfigParser()
    cf.read('../config.ini')
    timeout = int(cf.get('web', 'timeout'))

    r = requests.get(url, proxies=proxy, headers=headers, timeout=timeout)
    output = 'Code:{1}  Proxy:{2}  Url:{0}  '.format(url, r.status_code, proxy)
    print encode_wrap(output)

    if int(r.status_code) != 200:
        raise Exception('request fail')

    return r

# 获取IP代理地址(随机)
def get_proxies(ip_dataframe):

    if len(ip_dataframe) > 0:
        print 'IP proxy length:{0}'.format(len(ip_dataframe))
        index = random.randint(0, len(ip_dataframe))
        http = ip_dataframe.ix[index, 'Type']
        http = str(http).lower()
        ip = ip_dataframe.ix[index, 'IP']
        port = ip_dataframe.ix[index, 'Port']
        ip_proxy = "%s://%s:%s" % (http, ip, port)
        proxies = {http:ip_proxy}
        return proxies
    else:
        return {}