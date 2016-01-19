#coding:utf8

from tushare.stock import cons as ct
from tushare.stock import news_vars as nv
import pandas as pd
from datetime import datetime
import time
import lxml.html
from lxml import etree
import re
import json
from bs4 import BeautifulSoup as bs
from random import random
from multiprocessing.dummy import Pool as ThreadPool
from db_config import mysql_table_sina_finance

from util.webHelper import get_requests

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

from db_config import engine

def get_latest_news(date='2015-01-18', show_content=True):
    """
        获取即时财经新闻

    Parameters
    --------
        top:数值，显示最新消息的条数，默认为80条
        show_content:是否显示新闻内容，默认False

    Return
    --------
        DataFrame
            classify :新闻类别
            title :新闻标题
            time :发布时间
            url :新闻链接
            content:新闻内容（在show_content为True的情况下出现）
    """
    try:
        data_all = []
        for page in range(1, 100):
            URL = 'http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?col=43&spec=&type=&ch=03&date={date_}&k=&&offset_page=0&offset_num=0&num={count_}&asc=&page={page_}&r=0.{random_}'
            url = URL.format(date_ = date, count_=ct.PAGE_NUM[3], page_=page, random_=_random())
            print url
            request = Request(url)

            data_str = urlopen(request, timeout=10).read()
            data_str = data_str.decode('GBK')
            data_str = data_str.split('=')[1][:-1]
            data_str = eval(data_str, type('Dummy', (dict,),
                                           dict(__getitem__ = lambda s, n:n))())
            data_str = json.dumps(data_str)
            data_str = json.loads(data_str)
            data_str = data_str['list']
            data = []
            for r in data_str:
                rt = datetime.fromtimestamp(r['time'])
                rtstr = datetime.strftime(rt, "%Y-%m-%d %H:%M")
                arow = [r['channel']['title'], r['title'], rtstr, r['url']]
                #if show_content:
                #    arow.append(latest_content(r['url']))
                data.append(arow)


            #多线程
            pool = ThreadPool(processes=20)
            pool.map(_latest_content_for_multi, data)
            pool.close()
            pool.join()

            if data:
                data_all.extend(data)
            else:
                break

        df = pd.DataFrame(data_all, columns=nv.LATEST_COLS_C)
        df.to_sql(mysql_table_sina_finance, engine, if_exists='append', index=False)
        return df
    except Exception as er:
        print(str(er))


def _latest_content_for_multi(row_data):
    content = _latest_content_by_beautifulsoup(row_data[3], True)
    row_data.append(content)


def latest_content(url):

    stop = 3+ 2* random()
    time.sleep(stop)
    print "break:{:.3f}s".format(stop)
    content = _latest_content_xpath(url)
    if not content:
        content = _latest_content_by_beautifulsoup(url)
    return content

def _latest_content_xpath(url):
    '''
        获取即时财经新闻内容
    Parameter
    --------
        url:新闻链接

    Return
    --------
        string:返回新闻的文字内容
    '''
    try:
        html = lxml.html.parse(url)
        res = html.xpath('//div[@id=\"artibody\"]/p')
        if ct.PY3:
            sarr = [etree.tostring(node).decode('utf-8') for node in res]
        else:
            sarr = [etree.tostring(node) for node in res]
        sarr = ''.join(sarr).replace('&#12288;', '')#.replace('\n\n', '\n').
        html_content = lxml.html.fromstring(sarr)
        content = html_content.text_content()
        return content
    except Exception as er:
        print(str(er))

def _latest_content_by_beautifulsoup(url, has_proxy=False):
    '''
        获取即时财经新闻内容
    Parameter
    --------
        url:新闻链接

    Return
    --------
        string:返回新闻的文字内容
    '''
    try:
        r = get_requests(url, has_proxy=has_proxy)
        r.encoding = 'gbk'
        soup = bs(r.text, 'html5lib')
        print soup.encoding

        body = soup.find('div', {'id':'artibody'})
        sarr = []
        if not body:
            return ''

        p_all = body.find_all('p')
        for p in p_all:
            sarr.append(p.get_text())
        sarr = '\n'.join(sarr)
        print sarr
        return sarr

    except Exception as er:
        print(str(er))


def _random(n=16):
    from random import randint
    start = 10 ** (n - 1)
    end = (10 ** n) - 1
    return str(randint(start, end))

def run():
    #获取近三年的财经资讯
    df_date = pd.date_range('2015-01-01', '2016-01-18')
    for ix in range(len(df_date)):
        _date = str(df_date[ix])[:10]
        df =get_latest_news(_date)
        print df



if __name__ == "__main__":
    #_latest_content_by_beautifulsoup('http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?col=43&spec=&type=&ch=03&date=2015-01-01&k=&&offset_page=0&offset_num=0&num=100&asc=&page=3&r=0.4891643722918062')
    run()
    #df = get_latest_news(date='2016-01-01')
    #print df