# -*- coding:utf8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import MySQLdb
import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.proxy import *
from bs4 import BeautifulSoup
import re
import pandas as pd
from pandas import DataFrame
import requests
import random

from util.CodeConvert import *
from db_config import *



class XueQiu:

    def __init__(self):
        #self.driver = webdriver.Firefox()
        self.df_ip = pd.read_excel('../Data/ip_proxy_2015-11-25.xlsx','Sheet1') #ip代理地址库
        pass

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

    # 获取IP代理地址(随机)
    def get_proxies(self):

        if len(self.df_ip) > 0:
            print len(self.df_ip)
            index = random.randint(0, 2*len(self.df_ip)/3)
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
            print encode_wrap("使用代理:"), myProxy
        except Exception,e:
            print '没使用代理!'
            driver = webdriver.Firefox()
        return driver

    # 获取大V基本信息
    def get_BigV_Info(self, id):


        bigV = User()
        bigV.user_id = id
        if bigV.check_exists():
            print encode_wrap("id:%s 已经在数据库中" % id)
            #return

        try:
            url = 'http://xueqiu.com/%s' % str(id)
            print url

            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
            proxies = self.get_proxies()
            print '获取大V信息,使用代理:', proxies
            try:
                r = requests.get(url, headers=headers, proxies=proxies, timeout=5)
            except:
                try:
                    proxies = self.get_proxies()
                    print '连接超时,更换IP >>> 获取大V信息,使用代理:', proxies
                    r = requests.get(url, headers=headers, proxies=proxies, timeout=5)
                except:
                    print '连接超时,下次不使用代理 >>> 获取大V信息,不使用代理:', proxies
                    r = requests.get(url, headers=headers, timeout=5)

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
            print e




    # 获取投资组合
    def get_Investment_Portfolio(self):
        pass

    # 获取关注股票列表
    def get_Concerned_Stock_List(self):
        pass

    # 获取发布文章列表
    def get_publish_articles(self):
        pass

    # 获取关注列表
    def get_follow_list(self, id):
        try:

            url = 'http://xueqiu.com/%s' % str(id)
            try:
                driver = self.get_web_driver()
                driver.get(url)
            except Exception,e:
                driver.quit()
                print encode_wrap("超时1>>>更换代理")
                try:
                    driver = self.get_web_driver()
                    driver.get(url)
                except:
                    driver.quit()
                    print encode_wrap("超时2>>>不使用代理")
                    driver = webdriver.Firefox()
                    driver.get(url)

            driver.maximize_window()
            siz = driver.get_window_size()
            driver.set_window_size(siz['width'], siz['height']*2)


            # 模拟点击“关注”
            driver.find_element_by_xpath('//a[@href="#friends_content"]').click()


            f = open('show.html','w')
            f.write(driver.page_source)
            f.close()

            # 获取关注的总页码
            try:
                soup = BeautifulSoup(driver.page_source, 'html5lib')
                friendsDiv = soup.find('div', {'id':'friends_content'})
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

            #page_count = 1

            followList = []
            current_page = 1
            while(current_page < page_count+1):

                # pageLi = soup.find('li', {'class':'next'})
                # pageA = pageLi.find('a')
                # data_page = (int)(pageA['data-page'])-1
                print "Page:%d" % (current_page)

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
                                followList.append((name, href))

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


            # 获取关注的大V的信息
            for follow in followList:
                self.get_BigV_Info(follow[1])

            return followList


        except Exception,e:
            driver.quit()
            print e
            return []

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
                            'capacitys':[self.capacitys],
                            'summary':[self.summary],
                            'update_time':[self.update_time]
                            },
                           columns=['user_id', 'name', 'sex', 'area', 'stock_count', 'talk_count',
                                    'fans_count', 'capacitys', 'summary', 'update_time'])
            print df
            df.to_sql(big_v_table_mysql, engine, if_exists='append', index=False)
            return True
        except Exception,e:
            print e
            return False

if __name__ == "__main__":
    xueqiu = XueQiu()
    init_id ='1437016884' # 'ibaina'
    xueqiu.get_BigV_Info(init_id)



    follow_list = xueqiu.get_follow_list(init_id)

    search_floor = 1 # 搜索级数
    while(len(follow_list) > 0):
        s_xueqiu = GetNowTime() + encode_wrap('  递归级数:%d' % search_floor)
        print s_xueqiu
        f = open('xueqiu.log','w')
        f.write(s_xueqiu)
        f.close()

        f_list_all= []
        for _, follow_id in follow_list:
            f_list = xueqiu.get_follow_list(follow_id)
            f_list_all.extend(f_list)
        follow_list = f_list_all
        search_floor += 1
