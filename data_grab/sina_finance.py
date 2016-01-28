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
from db_config import mysql_table_sina_finance, mysql_table_unfinish_sina_news

from util.webHelper import get_requests
from util.codeConvert import GetNowTime

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

import requests

from db_config import engine

def get_latest_news(col='43', date='2015-01-18', page_start=1, page_end=100, show_content=True):
    """
        获取即时财经新闻

    Parameters
    --------
        top:数值，显示最新消息的条数，默认为80条
        date: str, 查询日期
        page_start: 起始页数
        page_end:终止页数
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
        for page in range(page_start, page_end):
            url = 'http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?col={_col}&spec=&type=&ch=03&date={date_}&k=&&offset_page=0&offset_num=0&num={count_}&asc=&page={page_}&r=0.{random_}'
            url = url.format(_col=col, date_ = date, count_=ct.PAGE_NUM[3], page_=page, random_=_random())
            print url
            request = Request(url)

            #r = requests.get(url, timeout=30)
            #data_str = r.text

            data_str = urlopen(request, timeout=1).read()
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


            # 多线程
            pool = ThreadPool(processes=20)
            pool.map(latest_content, data)
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
        df_er = pd.DataFrame([('sina_news', GetNowTime(), url)], columns=['site','date_occur','url'])
        df_er.to_sql(mysql_table_unfinish_sina_news, engine, if_exists='append')
        print(str(er))


def _latest_content_for_multi(row_data):
    content = _latest_content_by_beautifulsoup(row_data[3], True)
    row_data.append(content)


def latest_content(row_data):
    url = row_data[3]
    stop = 3+ 2* random()
    #time.sleep(stop)
    #print "break:{:.3f}s".format(stop)
    content = _latest_content_xpath(url)
    if not content:
        content = _latest_content_by_beautifulsoup(url)
    row_data.append(content)

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
        if 'video.sina.com.cn' in url:
            return ''
        html = lxml.html.parse(url)
        res = html.xpath('//div[@id=\"artibody\"]/p')
        if ct.PY3:
            sarr = [etree.tostring(node).decode('utf-8') for node in res]
        else:
            sarr = [etree.tostring(node) for node in res]
        sarr = ''.join(sarr).replace('&#12288;', '')#.replace('\n\n', '\n').
        html_content = lxml.html.fromstring(sarr)
        content = html_content.text_content()

        print content
        print 'xpath:%s' % url

        return content
    except Exception as er:
        print 'xpath:', (str(er))

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
        if 'video.sina.com.cn' in url:
            return ''

        r = get_requests(url, has_proxy=has_proxy)
        r.encoding = 'gbk'
        soup = bs(r.text, 'lxml')
        body = soup.find('div', {'id':'artibody'})
        sarr = []
        if not body:
            soup = bs(r.text, 'html5lib')
            body = soup.find('div', {'id':'artibody'})
            if not body:
                return ''

        p_all = body.find_all('p')
        for p in p_all:
            sarr.append(p.get_text())
        sarr = '\n'.join(sarr)

        print sarr
        print 'bs:%s' % url

        return sarr

    except Exception as er:
        print 'beautifusoup:', (str(er))
        return ''


def _random(n=16):
    from random import randint
    start = 10 ** (n - 1)
    end = (10 ** n) - 1
    return str(randint(start, end))

def run_unfinish_news_list():
    """
    重新获取抓取失败的新闻列表
    :return:
    """
    sql = 'select * from {_table}'.format(_table=mysql_table_unfinish_sina_news)
    df = pd.read_sql(sql, engine)
    for ix, row in df.iterrows():
        url = row['url']
        print url
        result = re.findall(r'col=([\w,]+).*?&date=([\d+-]+).*?&page=(\d+)', url)
        if len(result):
            col = result[0][0]
            date_s = result[0][1]
            page_count = int(result[0][2])

            get_latest_news(col=col, date=date_s, page_start=page_count)

def run_unfinish_content_is_null():
    """
    重新获取内容空缺的文章
    :return:
    """
    sql = 'select classify, url from {_table} where length(content)=0 limit 10'.format(_table=mysql_table_sina_finance)
    df = pd.read_sql(sql, engine)
    for ix, row in df.iterrows():
        content = _latest_content_by_beautifulsoup(row['url'])
        if content:
            sql = 'update {0} set content= "{1}" where classify="{2}" and url="{3}"'.format(mysql_table_sina_finance, content, row['classify'], row['url'])
            print sql
            engine.execute(sql)


def run_finance_news():
    #获取近三年的财经资讯
    df_date = pd.date_range('2013-01-01', '2013-12-31')
    for ix in range(len(df_date)):
        _date = str(df_date[ix])[:10]
        col = '43'
        df =get_latest_news(col, _date)
        print df

def run_other_news():
    #获取近三年的其他资讯
    df_date = pd.date_range('2015-01-01', '2016-01-27')
    for ix in range(len(df_date)):
        _date = str(df_date[ix])[:10]
        col = '90,91,92,94,95,93,96' # 国内,国际,社会,体育,娱乐,军事,科技
        df =get_latest_news(col, _date)
        print df


if __name__ == "__main__":
    #url = 'http://video.sina.com.cn/p/finance/china/20151124/160565135995.html '
    #_latest_content_by_beautifulsoup(url, True)
    #run_finance_news()
    #run_other_news()
    #run_unfinish_news_list()
    run_unfinish_content_is_null()