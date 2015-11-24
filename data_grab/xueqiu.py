# -*- coding:utf8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import MySQLdb
import ConfigParser
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import pandas as pd
from pandas import DataFrame
import requests

from util.CodeConvert import *
from db_config import *

class XueQiu:

    def __init__(self):
        self.driver = webdriver.Firefox()
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



    # 获取大V基本信息
    def get_BigV_Info(self, id):

        try:
            url = 'http://xueqiu.com/%s' % str(id)
            print url
            # r = requests.get(url)
            # print r.text

            self.driver.get(url)
            #driver.get_screenshot_as_file("show.png")

            bigV = User()
            bigV.user_id = id

            soup = BeautifulSoup(self.driver.page_source)

            info = soup.find('div', {'class':'profile_info_content'})
            bigV.name = info.find('span').get_text()

            sexAndArea = info.find('li', {'class':'gender_info'}).get_text()
            sexArea = sexAndArea.split()
            if len(sexArea) > 2:
                bigV.sex, bigV.area = sexArea[0], sexArea[1]

            stockInfo = info.findAll('li')[1].get_text()

            p = re.compile(r'(\d+)')
            group = p.findall(stockInfo)
            print group
            if len(group) == 3:
                bigV.stock_count = group[0]
                bigV.talk_count = group[1]
                bigV.fans_count = group[2]

            try:
                capacityDiv = info.find('div', {'class':'item_content discuss_stock_list'})
                bigV.capacitys = capacityDiv.get_text()
            except Exception,e:
                print '能力圈不存在'

            try:
                summaryP = info.find('p', {'class':'detail'})
                summary = summaryP.get_text()
                bigV.summary = summary.replace(r'收起', '')
            except Exception,e:
                print '简介不存在'

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
            self.driver.get(url)

            # 模拟点击“关注”
            self.driver.find_element_by_xpath('//a[@href="#friends_content"]').click()


            f = open('show.html','w')
            f.write(self.driver.page_source)
            f.close()

            # 获取关注的总页码
            try:
                soup = BeautifulSoup(self.driver.page_source, 'html5lib')
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

            page_count = 1

            followList = []
            current_page = 1
            while(current_page < page_count+1):

                # pageLi = soup.find('li', {'class':'next'})
                # pageA = pageLi.find('a')
                # data_page = (int)(pageA['data-page'])-1
                print "Page:%d" % (current_page)

                # add friends where follows>1000
                userAll = soup.find('ul', {'class':'users-list'})
                userList = userAll.findAll('li')
                for user in userList:
                    href = user.find('a')['href'].replace('/', '')
                    name = user.find('a')['data-name']

                    userInfo = user.find('div', {'class':'userInfo'}).get_text()
                    m = re.search(u'粉丝(\d+)', userInfo)
                    if m:
                        print name, href, m.group(0)
                        fans_count = int(m.group(1))
                        if fans_count >= 1000:
                            followList.append((name, href))

                try:
                    UserListElement = self.driver.find_element_by_xpath('//ul[@class="users-list"]')
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

                    soup = BeautifulSoup(self.driver.page_source, 'html5lib')
                    current_page += 1

                except Exception,e:
                    print e
                    break

            print 'fans count:', len(followList)


            # 获取关注的大V的信息
            for follow in followList:
                self.get_BigV_Info(follow[1])

            return followList

            # 递归
            # for follow in followList:
            #     self.get_follow_list(follow[1])


        except Exception,e:
            #self.driver.quit()
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

    def to_mysql(self):

        try:

            # 排除已存在的数据
            try:
                query_sql = "select * from %s where user_id='%s'" % (big_v_table_mysql, self.user_id)
                df_query = pd.read_sql_query(query_sql, engine)
                if len(df_query) > 0:
                    return False
            except Exception,e:
                print '表格不存在', e

            df = DataFrame({'user_id':[self.user_id],
                            'name':[self.name],
                            'area':[self.area],
                            'stock_count':[self.stock_count],
                            'talk_count':[self.talk_count],
                            'fans_count':[self.fans_count],
                            'capacitys':[self.capacitys],
                            'summary':[self.summary],
                            'update_time':[self.update_time]
                            },
                           columns=['user_id', 'name', 'area', 'stock_count', 'talk_count', 'fans_count', 'capacitys', 'summary', 'update_time'])
            print df
            df.to_sql(big_v_table_mysql, engine, if_exists='append', index=False)
            return True
        except Exception,e:
            print e
            return False

if __name__ == "__main__":
    xueqiu = XueQiu()
    init_id = 'ibaina'
    xueqiu.get_BigV_Info(init_id)
    follow_list = xueqiu.get_follow_list(init_id)

    search_floor = 1 # 搜索级数
    while(len(follow_list) > 0):
        s_xueqiu = GetNowTime() + '  递归级数:%d' % search_floor
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

    xueqiu.driver.quit()