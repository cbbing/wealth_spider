# -*- coding:utf8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import platform
if platform.system() == 'Windows':
    sys.path.append('D:/Code/wealth_spider')
else:
    sys.path.append('/Users/cbb/Documents/pythonspace/wealth_spider')

import MySQLdb
import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.proxy import *
from bs4 import BeautifulSoup
import re
import pandas as pd
from pandas import DataFrame, Series
import requests
import random
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool

from util.CodeConvert import *
from db_config import *
from IPProxy.ip_proxy import IP_Proxy
from util.helper import fn_timer



class XueQiu:

    def __init__(self):
        #self.driver = webdriver.Firefox()
        #self.df_ip = pd.read_excel('../Data/ip_proxy_2015-11-25.xlsx','Sheet1') #ip代理地址库

        ip_file = "../Data/ip_proxy_%s.csv" % GetNowDate()
        try:
            self.df_ip = pd.read_csv(ip_file)
        except:
            print 'not exist:%s, get it now!' % ip_file
            ip_proxy = IP_Proxy()
            ip_proxy.run()
            self.df_ip = pd.read_csv(ip_file)

        self.init_time = time.time()

        self.site = 'http://xueqiu.com'
        self.sleep_time = 5  # second

        #self.init_database()

    def init_database(self):
        try:

            cf = ConfigParser.ConfigParser()
            cf.read('../config.ini')
            host = cf.get('mysql', 'host')
            port = int(cf.get('mysql', 'port'))
            db = cf.get('mysql', 'db')
            user = cf.get('mysql', 'user')
            pwd = cf.get('mysql', 'pwd')

            conn=MySQLdb.connect(host=host,user=user,passwd=pwd,port=port)
            cur=conn.cursor()

            cur.execute('create database if not exists %s' % db)
            conn.select_db(db)
            #cur.execute('create table test(id int,info varchar(20))')

            # value=[1,'hi rollen']
            # cur.execute('insert into test values(%s,%s)',value)
            #
            # values=[]
            # for i in range(20):
            #     values.append((i,'hi rollen'+str(i)))
            #
            # cur.executemany('insert into test values(%s,%s)',values)
            #
            # cur.execute('update test set info="I am rollen" where id=3')

            conn.commit()
            cur.close()
            conn.close()

        except MySQLdb.Error,e:
             print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    # 更新IP代理库
    def update_ip_data(self):
        ip_file = "../Data/ip_proxy_%s.csv" % GetNowDate()
        ip_proxy = IP_Proxy()
        ip_proxy.run()
        self.df_ip = pd.read_csv(ip_file)

    # 获取IP代理地址(随机)
    def get_proxies(self):

        if len(self.df_ip) > 0:
            print len(self.df_ip)
            index = random.randint(0, len(self.df_ip))
            http = self.df_ip.ix[index, 'Type']
            http = str(http).lower()
            ip = self.df_ip.ix[index, 'IP']
            port = self.df_ip.ix[index, 'Port']
            ip_proxy = "%s://%s:%s" % (http, ip, port)
            proxies = {http:ip_proxy}
            return proxies
        else:
            return {}

    def get_web_driver(self):
        driver = webdriver.Firefox()
        return driver

        try_times = 3
        while (try_times > 0):

            try:
                proxies = self.get_proxies()
                if proxies.has_key('http'):
                    myProxy = proxies['http']
                elif proxies.has_key('https'):
                    myProxy = proxies['https']

                proxy = Proxy({
                   'proxyType': ProxyType.MANUAL,
                    'httpProxy': myProxy,
                    'ftpProxy': myProxy,
                    'sslProxy': myProxy,
                    'noProxy': ''
                })
                driver = webdriver.Firefox(proxy=proxy)
                driver.set_page_load_timeout(10)
                driver.get('http://www.baidu.com')
                print encode_wrap("使用代理:"), myProxy
                return driver
            except Exception,e:
                print encode_wrap('连接超时, 重试%s' % (3 - try_times + 1))
                try_times -= 1
                try:
                    driver.quit()
                except:
                    None


        return None


    def get_request(self, url):

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}

        try_times = 3
        while (try_times > 0):

            proxies = self.get_proxies()
            print encode_wrap( '获取大V信息:%s:使用代理:' % url), proxies
            try:
                r = requests.get(url, headers=headers, proxies=proxies, timeout=5)
                return r
            except:
                if proxies.has_key('http'):
                    myProxy = proxies['http']
                elif proxies.has_key('https'):
                    myProxy = proxies['https']
                m =re.search('//([\d\.]+):', myProxy)
                if m:
                    ip = m.group(1)
                    #self.df_ip

                print encode_wrap('连接超时, 重试%s' % (3 - try_times + 1))
                try_times -= 1


    # 获取大V基本信息
    def get_BigV_Info(self, id):

        bigV = User()
        bigV.user_id = id
        if bigV.check_exists():
            print encode_wrap("id:%s 已经在数据库中" % id)
            return True

        try:
            url = 'http://xueqiu.com/%s' % str(id)
            print url
            r = self.get_request(url)
            soup = BeautifulSoup(r.text, 'html5lib')

            info = soup.find('div', {'class':'profile_info_content'})
            bigV.name = info.find('span').get_text()

            sexAndArea = info.find('li', {'class':'gender_info'}).get_text()
            sexArea = sexAndArea.split()
            if len(sexArea) >= 2:
                bigV.sex, bigV.area = sexArea[0], sexArea[1]
            elif len(sexArea) == 1:
                if sexArea[0] in ['男', '女', '保密']:
                    bigV.sex = sexArea[0]

            stockInfo = info.findAll('li')[1].get_text()

            m = re.search(u'股票(\d+)', stockInfo)
            if m:
                bigV.stock_count = m.group(1)

            m = re.search(u'讨论(\d+)', stockInfo)
            if m:
                bigV.talk_count = m.group(1)

            m = re.search(u'粉丝(\d+)', stockInfo)
            if m:
                bigV.fans_count = m.group(1)

            try:
                capacityDiv = info.find('div', {'class':'item_content discuss_stock_list'})
                bigV.capacitys = capacityDiv.get_text()
            except Exception,e:
                print encode_wrap('能力圈不存在')

            try:
                summaryP = info.find('p', {'class':'detail'})
                summary = summaryP.get_text()
                bigV.summary = summary.replace(r'收起', '')
            except Exception,e:
                print encode_wrap('简介不存在')

            bigV.update_time = GetNowTime()

            bigV.to_mysql()

        except Exception,e:
            se = Series([id, GetNowTime(), str(e)], index=['user_id', 'fail_time', 'fail_reason'])
            df = DataFrame(se).T
            df.to_sql(unfinish_big_v_table_mysql, engine, if_exists='append', index=False)
            print e
            return False

        return True


    # 获取投资组合
    def get_Investment_Portfolio(self):
        pass

    # 获取关注股票列表
    def get_Concerned_Stock_List(self):
        pass



    # 获取关注列表
    def get_follow_list(self, id):
        try:
            #过滤已走路径
            query = "select follow_search_time from %s where user_id='%s'" % (big_v_table_mysql, id )
            df_query = pd.read_sql_query(query, engine)
            if len(df_query) > 0 :
                data = df_query.ix[0, 'follow_search_time']
                if not data is None and len(df_query.ix[0, 'follow_search_time']) > 0:
                    print 'have get follow (%s)' % id
                    return

            # 定期更换IP代理库
            s1 = time.time()
            if (s1 - self.init_time) > 8 * 60 * 60:
                print '更换IP代理库'
                self.update_ip_data()
                self.init_time = time.time()


            url = 'http://xueqiu.com/%s' % str(id)
            driver = self.get_web_driver()
            driver.get(url)

            driver.maximize_window()
            siz = driver.get_window_size()
            driver.set_window_size(siz['width'], siz['height']*2)

            # 模拟点击“关注”
            driver.find_element_by_xpath('//a[@href="#friends_content"]').click()

            # f = open('show.html','w')
            # f.write(driver.page_source)
            # f.close()

            # 获取关注的总页码
            soup = BeautifulSoup(driver.page_source, 'html5lib')
            page_count = self.get_page_count(soup, 'friends_content')

            #page_count = 1

            followList = []
            current_page = 1
            while(current_page < page_count+1):

                # pageLi = soup.find('li', {'class':'next'})
                # pageA = pageLi.find('a')
                # data_page = (int)(pageA['data-page'])-1
                print "Page:%d / %d" % (current_page, page_count)

                try:
                    # add friends where follows>1000

                    userAll = soup.find('ul', {'class':'users-list'})
                    userList = userAll.findAll('li')
                    for user in userList:
                        href = user.find('a')['href'].replace('/', '')
                        name = user.find('a')['data-name']

                        userInfo = user.find('div', {'class':'userInfo'}).get_text()
                        m = re.search(u'粉丝(\d+)', userInfo)
                        if m:
                            print encode_wrap(name), href, encode_wrap(m.group(0))
                            fans_count = int(m.group(1))
                            if fans_count >= 1000:
                                followList.append(href)

                    # 点击下一页
                    try:
                        UserListElement = driver.find_element_by_xpath('//ul[@class="users-list"]')
                        btn_nexts = UserListElement.find_elements_by_xpath('//ul[@class="pager"]//a[@data-page="%d"]' % current_page)

                        #NextElement = UserListElement.find_element_by_xpath('//li[@class="next"]')
                        #btn_nexts = NextElement.find_elements_by_xpath('//a[@data-page="%d"]' % current_page)

                        for btn_next in btn_nexts:
                            if btn_next.is_displayed():
                                btn_next.click()
                                print 'click follows page:%d' % current_page
                                break
                            else:
                                print 'next button  no show'

                        soup = BeautifulSoup(driver.page_source, 'html5lib')
                        current_page += 1
                        time.sleep(3)

                    except Exception,e:
                        print e
                        break
                except Exception,e:
                    print e
                    break

            print 'fans count:', len(followList)
            driver.quit()

            # 标记已搜寻关注列表
            sql = 'update %s set follow_search_time = "%s" where user_id = "%s"' % (big_v_table_mysql, GetNowTime(), id)
            engine.execute(sql)


            # 获取关注的大V的信息
            #多线程
            pool = ThreadPool(processes=4)
            pool.map(self.get_BigV_Info, followList)
            pool.close()
            pool.join()

            # for follow in followList:
            #     self.get_BigV_Info(follow)

            # 粉丝中的大V列表
            self.get_big_v_in_fans(followList, id)

            return followList


        except Exception,e:
            print e
            return []

    def get_publish_articles(self):
        t1 = time.time()
        print 'begin query...'
        #sql = 'select distinct user_id from %s where user_id not in (select distinct user_id from %s)' % (big_v_table_mysql, archive_table_mysql)
        #df = pd.read_sql_query(sql, engine)
        sql1 = 'select distinct user_id from %s where fans_count > 10000' % (big_v_table_mysql)
        sql2 = 'select distinct user_id from %s' % archive_table_mysql
        df1 = pd.read_sql_query(sql1, engine)
        df2 = pd.read_sql_query(sql2, engine)
        user_ids1 = df1['user_id'].get_values()
        user_ids2 = df2['user_id'].get_values()
        user_ids = [id for id in set(user_ids1).difference(user_ids2)]
        t2 = time.time()
        print 'query mysql by join cose:', t2-t1, 's'
        #user_ids = df['user_id'].get_values()
        for user_id in user_ids:
            try:
                self.get_publish_articles_by_id(user_id)
            except Exception, e:
                se = Series([user_id, GetNowTime(), str(e)], index=['user_id', 'fail_time', 'fail_reason'])
                df = DataFrame(se).T
                df.to_sql(unfinish_arcticle_table_mysql, engine, if_exists='append', index=False)
                print e



    # 获取发布文章列表
    def get_publish_articles_by_id(self, id):
        url = 'http://xueqiu.com/%s' % str(id)
        driver = self.get_web_driver()
        driver.get(url)

        driver.maximize_window()
        siz = driver.get_window_size()
        driver.set_window_size(siz['width'], siz['height']*2)

        # 模拟点击“主贴”,切换到"原发布"
        driver.find_element_by_xpath('//a[@href="#status_content"]').click()
        time.sleep(1)
        driver.find_element_by_xpath('//a[@href="#status_content" and @data-text="原发布"]').click()

        # 获取原发布的总页码
        soup = BeautifulSoup(driver.page_source, 'html5lib')
        page_count = self.get_page_count(soup, 'statusLists')

        # 获取每页文章列表
        current_page = 1
        while(current_page < page_count+1):
            print "Page:%d / %d" % (current_page, page_count)

            archiveList = self.get_archive_list_in_one_page(soup, id)

            # 存入mysql
            #[archive.to_mysql() for archive in archiveList if not archive.check_exists()]
            [archive.to_mysql() for archive in archiveList] #不需判断数据库是否存在,若存在则抛出异常,不插入

            # 判断文章是否为最近一年发布，若否则不继续搜索
            if len(archiveList) > 0:
                archive = archiveList[-1]

                nowDate = GetNowTime2()
                now_year = int(nowDate[:4])
                last_year = nowDate.replace(str(now_year), str(now_year-1)) # 去年今日
                if archive.publish_time < last_year:
                    break

            # 点击下一页
            clickStatus = self.click_next_page(driver,'//ul[@class="status-list"]', current_page)
            if clickStatus:
                soup = BeautifulSoup(driver.page_source, 'html5lib')
                current_page += 1
                time.sleep(self.sleep_time)
            else:
                print encode_wrap('点击下一页出错, 退出...')
                break


        driver.quit()



    # 获取粉丝中的大V
    def get_big_v_in_fans(self, followList, id):

        try:
            df = DataFrame({'user_id':followList, #被关注者
                            'fans_id':id                            #关注者
                            }, columns=['user_id', 'fans_id'])
            print df[:10]
            df.to_sql(fans_in_big_v_table_mysql, engine, if_exists='append', index=False)

        except Exception,e:
            print e

    # 从未完成列表中继续搜索
    def get_unfinished_big_v(self):
        sql1 = "select distinct user_id from %s where length(follow_search_time) = 0" % (big_v_table_mysql)
        sql2 = "select distinct user_id from %s" % unfinish_big_v_table_mysql
        df1 = pd.read_sql_query(sql1, engine)
        df2 = pd.read_sql_query(sql2, engine)
        print 'df1:%d, df2:%d' % (len(df1), len(df2))
        df = pd.merge(df1,df2, how='outer')
        print "unfinish list len:", len(df)
        user_ids = df['user_id'].get_values()
        for user_id in user_ids:
            result = self.get_BigV_Info(user_id)
            self.get_follow_list(user_id)
            if result:
                engine.execute("delete from %s where user_id='%s'" % (unfinish_big_v_table_mysql, user_id))
                print encode_wrap('删除未完成列表的user_id')

    # 计算大V排名
    def calcute_big_v_rank(self):
        factor_fans = 0.5
        factor_big_v_in_fans = 0.1
        factor_arcticle = 0.3
        factor_comments = 0.2

        scores = []

        sql_bigv = "select user_id, fans_count from %s where fans_count > 10000" % big_v_table_mysql;
        df_bigv = pd.read_sql_query(sql_bigv, engine)
        for i in range(len(df_bigv)):
            #print df_bigv
            user_id = df_bigv.ix[i, 'user_id']
            fans_count = int(df_bigv.ix[i,'fans_count'])
            sql_bigv_in_fans = "SELECT count(*) as BigVFansCount FROM %s where user_id = '%s'" % (fans_in_big_v_table_mysql, user_id)
            df_bigv_in_fans = pd.read_sql_query(sql_bigv_in_fans, engine)
            if len(df_bigv_in_fans):
                bigvfans_count = df_bigv_in_fans.ix[0, 'BigVFansCount']
            else:
                bigvfans_count = 0

            sql_arcticle = "select count(*) as ArticleCount , sum(comment_count) as CommentCount from %s where user_id='%s'" % (archive_table_mysql, user_id)
            df_arcticle = pd.read_sql_query(sql_arcticle, engine)
            if len(df_arcticle):
                article_count = df_arcticle.ix[0, 'ArticleCount']
                comment_count = df_arcticle.ix[0, 'CommentCount']
            else:
                article_count = 0
                comment_count = 0

            score = factor_fans * fans_count + factor_big_v_in_fans *  bigvfans_count + factor_arcticle * article_count + factor_comments * comment_count
            scores.append((score, user_id))

        scores = sorted(scores)[-1::-1]
        print '前十名:'
        print scores[:10]

    # 分词提取
    def word_seg(self):
        sql = "select user_id, detail from %s " % (archive_table_mysql)
        df = pd.read_sql_query(sql, engine)
        for i in range(len(df)):
            user_id = df.ix[i, 'user_id']
            detail = df.ix[i, 'detail']




    ### 类中的辅助函数

    # 获取总页码
    def get_page_count(self, soup, tpye_id):

        try:
            friendsDiv = soup.find('div', {'id':tpye_id})
            pagerUL = friendsDiv.find('ul', {'class':'pager'})
            data_pages = pagerUL.find_all('a')
            page_count = 0
            for a in data_pages:
                cur_count = (int)(a['data-page'])
                if cur_count > page_count:
                    page_count = cur_count
        except Exception,e:
            # 只有一页
            page_count = 1
        return  page_count


    # 点击下一页
    def click_next_page(self, driver, xpath,  current_page):
        try:
            UserListElement = driver.find_element_by_xpath(xpath)
            # btn_nexts 找不到唯一的,但只有一个按钮显示,故依次点击,点击成功就马上返回
            btn_nexts = UserListElement.find_elements_by_xpath('//ul[@class="pager"]//a[@data-page="%d"]' % current_page)

            for btn_next in btn_nexts:
                if btn_next.is_displayed():
                    btn_next.click()
                    print 'click follows page:%d' % current_page
                    return True
                else:
                     print 'next button  no show'
        except Exception,e:
            print e
            return False

        return False

    # 获取一页中的文章列表
    def get_archive_list_in_one_page(self, soup, id):

        archiveList = []

        statusAll = soup.find('ul', {'class':'status-list'})
        statusList = statusAll.findAll('li')
        for status in statusList:

            try:

                archive = Article()
                archive.user_id = id

                archive.detail = status.find('div', {'class':'detail'}).get_text()
                infos = status.find('div', {'class':'infos'})
                archive.publish_time = archive.regularization_time(infos.find('a', {'class':'time'}).get_text())
                archive.device = infos.find('span').get_text().replace('来自', '')

                try:
                    # 若存在标题
                    titleH4 = status.find('h4')
                    archive.title = titleH4.find('a').get_text()
                    archive.href = self.site + titleH4.find('a')['href']
                except:
                    print 'no title and href'

                ops = status.find('div', {'class':'ops'})
                repost = ops.find('a', {'class':'repost second'}).get_text()
                donate = ops.find('a', {'class':'donate'}).get_text()
                comment = ops.find('a', {'class':'statusComment last'}).get_text()
                archive.repost_count = repost.replace('转发', '').replace('(','').replace(')','')
                archive.donate_count = donate.replace('赞助', '').replace('(','').replace(')','')
                archive.comment_count = comment.replace('评论', '').replace('(','').replace(')','')

                archiveList.append(archive)

            except Exception, e:
                print e

        return archiveList


class User:
    def __init__(self):
        self.user_id = ''
        self.name = ''
        self.sex = ''
        self.area = ''
        self.stock_count = 0
        self.talk_count = 0
        self.fans_count = 0
        self.capacitys = ''
        self.summary = ''
        self.update_time = ''

    # 检测id是否已经存在于数据库中
    def check_exists(self):

        try:
            query_sql = "select * from %s where user_id='%s'" % (big_v_table_mysql, self.user_id)
            df_query = pd.read_sql_query(query_sql, engine)
            if len(df_query) > 0:
                return True
            else:
                return False

        except Exception,e:
            print encode_wrap('数据库中表不存在:%s' % big_v_table_mysql)
            return False

    def to_mysql(self):

        try:

            df = DataFrame({'user_id':[self.user_id],
                            'name':[self.name],
                            'sex': [self.sex],
                            'area':[self.area],
                            'stock_count':[self.stock_count],
                            'talk_count':[self.talk_count],
                            'fans_count':[self.fans_count],
                            'big_v_in_fans_count':0,
                            'follows_count':0,
                            'capacitys':[self.capacitys],
                            'summary':[self.summary],
                            'follow_search_time':'',
                            'update_time':[self.update_time]
                            },
                           columns=['user_id', 'name', 'sex', 'area', 'stock_count', 'talk_count',
                                    'fans_count', 'big_v_in_fans_count', 'follows_count', 'capacitys',
                                    'summary', 'follow_search_time', 'update_time'])
            print df
            df.to_sql(big_v_table_mysql, engine, if_exists='append', index=False)
            return True
        except Exception,e:
            print e
            return False

# 文章
class Article:
    def __init__(self):
        self.user_id = ''
        self.title = ''
        self.detail = ''
        self.publish_time = ''
        self.device = ''
        self.href = ''
        self.repost_count = 0  # 转发数
        self.donate_count = 0  # 赞助数
        self.comment_count = 0 # 评论数



    # 检测id是否已经存在于数据库中
    def check_exists(self):

        try:
            # if not os.path.exists('../Data/Temp'):
            #     os.mkdir('../Data/Temp')
            # filename = '../Data/Temp/query_exists.json'

            # if os.path.exists(filename):
            #     df_query = pd.read_json(filename)
            #     print df_query[:10]
            # else:

            query_sql = "select * from %s where user_id='%s' and publish_time='%s'" % (archive_table_mysql, self.user_id, self.publish_time)
            df_query = pd.read_sql_query(query_sql, engine)
            print df_query[:10]
                #df_query.to_json(filename)


            if len(df_query) > 0:
                return True
            else:
                return False

        except Exception,e:
            print encode_wrap('数据库中表不存在:%s' % big_v_table_mysql)
            return False

    # 规整化发表时间
    def regularization_time(self, publish_time):
        now = GetNowDate()
        if '今天' in publish_time:
            publish_time = publish_time.replace('今天', now)
        elif len(publish_time) == 11:
            publish_time = time.strftime("%Y-",time.localtime(time.time())) + publish_time

        return publish_time


    def to_mysql(self):

        try:

            df = DataFrame({'user_id':[self.user_id],
                            'title':[self.title],
                            'detail': [self.detail],
                            'publish_time':[self.publish_time],
                            'device':[self.device],
                            'href':[self.href],
                            'repost_count':[self.repost_count],
                            'donate_count':[self.donate_count],
                            'comment_count':[self.comment_count]
                            },
                           columns=['user_id', 'title', 'detail',
                                    'publish_time', 'repost_count', 'donate_count',
                                    'comment_count', 'device', 'href'])
            print df
            df.to_sql(archive_table_mysql, engine, if_exists='append', index=False)
            return True

        except Exception,e:
            print e
            return False

if __name__ == "__main__":


    xueqiu = XueQiu()
    #xueqiu.get_unfinished_big_v()
    xueqiu.get_publish_articles()
    #xueqiu.calcute_big_v_rank()
    exit(0)

    init_id = 'zzx8964' # 'ibaina'
    xueqiu.get_BigV_Info(init_id)

    follow_list = xueqiu.get_follow_list(init_id)
    if follow_list is None:
        print encode_wrap('已查询过关注列表,程序退出')
        exit(0)

    search_floor = 1 # 搜索级数
    while(len(follow_list) > 0):
        s_xueqiu = GetNowTime() + encode_wrap('  递归级数:%d' % search_floor)
        print s_xueqiu
        f = open('xueqiu.log','a')
        f.write(s_xueqiu + '\n')
        f.close()

        f_list_all= []
        for follow_id in follow_list:
            f_list = xueqiu.get_follow_list(follow_id)
            if not f_list is None:
                f_list_all.extend(f_list)
        follow_list = f_list_all
        search_floor += 1
