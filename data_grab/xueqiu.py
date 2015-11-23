# -*- coding:utf8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import MySQLdb
import ConfigParser
from selenium import webdriver
from bs4 import BeautifulSoup
import re


class XueQiu:

    def __init__(self):
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
    def get_BigV_Info(self):
        driver = webdriver.Firefox()
        url = 'http://xueqiu.com/3037882447'
        driver.get(url)
        driver.get_screenshot_as_file("show.png")

        soup = BeautifulSoup(driver.page_source)
        info = soup.find('div', {'class':'profile_info_content'})
        name = info.find('span').get_text()

        sexAndArea = info.find('li', {'class':'gender_info'}).get_text()
        sex, area = sexAndArea.split()

        stockInfo = info.findAll('li')[1].get_text()

        p = re.compile(r'(\d+)')
        group = p.findall(stockInfo)
        print group
        if len(group) == 3:
            stockNum = group[0]
            talks = group[1]
            fans = group[2]

        capacityDiv = info.find('div', {'class':'item_content discuss_stock_list'})
        capacitys = capacityDiv.get_text()

        summaryP = info.find('p', {'class':'detail'})
        summary = summaryP.get_text()
        summary = summary.replace(r'收起', '')


        driver.quit()

        pass

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
    def get_follow_list(self):
        try:
            driver = webdriver.Firefox()
            url = 'http://xueqiu.com/3037882447'
            driver.get(url)

            # 模拟点击“关注”
            driver.find_element_by_xpath('//a[@href="#friends_content"]').click()


            f = open('show.html','w')
            f.write(driver.page_source)
            f.close()

            followList = []

            soup = BeautifulSoup(driver.page_source, 'html5lib')
            userAll = soup.find('ul', {'class':'users-list'})
            userList = userAll.findAll('li')
            for user in userList:
                href = user.find('a')['href'].replace('/', '')
                name = user.find('a')['data-name']
                print name, href

                userInfo = user.find('div', {'class':'userInfo'}).get_text()
                m = re.search(u'粉丝(\d+)', userInfo)
                if m:
                    print m.group(0)
                    fans_count = int(m.group(1))
                    if fans_count >= 1000:
                        followList.append((name, href))

            print followList




            driver.quit()
        except Exception,e:
            driver.quit()
            print e

if __name__ == "__main__":
    xueqiu = XueQiu()
    #xueqiu.get_BigV_Info()
    xueqiu.get_follow_list()