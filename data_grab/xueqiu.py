# -*- coding:utf8 -*-

import MySQLdb
import ConfigParser
from selenium import webdriver

class XueQiu:

    def __init__(self):
        self.init_database()

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
        driver = webdriver.PhantomJS()
        url = 'http://xueqiu.com/3037882447'
        driver.get(url)
        driver.get_screenshot_as_file("xueqiu.png")

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

if __name__ == "__main__":
    xueqiu = XueQiu()
    xueqiu.get_BigV_Info()