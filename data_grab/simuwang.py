#coding: utf-8

from selenium import webdriver
from bs4 import BeautifulSoup as bs
import pandas as pd
import time

from db_config import engine


class Item():

    def __init__(self):
        self.product = ''  # 产品名称
        self.product_url = '' #产品链接
        self.guwen = ''  # 投资顾问
        self.guwen_url = '' #投顾链接
        self.date_jingzhi = ''  # 净值日期
        self.unit_jingzhi = ''  # 单位净值
        self.sum_jingzhi = ''  # 累计净值
        self.sum_earn = ''  # 累计收益
        self.year_earn = ''  # 年化收益
        self.prechange = ''  # 净值变动

    def __str__(self):
        return "{} {} {} {} {} {} {} {}".format(self.product, self.guwen, self.date_jingzhi, self.unit_jingzhi,
                                                self.sum_jingzhi, self.sum_earn, self.year_earn, self.prechange)

class Simuwang():

    def __init__(self):
        self.site = 'http://dc.simuwang.com'

    def get_jingzhi(self):
        url = 'http://dc.simuwang.com/nav.html'
        dr = webdriver.Firefox()
        dr.maximize_window()

        dr.get(url)
        # time.sleep(5)
        #
        # dr.find_element_by_link_text('已有账号?立即登录 >>').click()
        # time.sleep(3)
        #
        # dr.find_element_by_xpath('//input[@type="text"]').send_keys('18410182275')
        # dr.find_element_by_xpath('//input[@type="password"]').send_keys('357959')
        #
        # dr.find_element_by_xpath('//input[@type="submit"]').click()



        for i in range(338,667):
            self.parse_page_data(dr)
            print 'page:{}'.format(i + 1)
            dr.find_element_by_link_text('下一页').click()




    def parse_page_data(self, dr):
        items = []

        soup = bs(dr.page_source, 'lxml')
        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) < 12 or tds[1].text == '产品名称':
                continue

            item = Item()

            item.product = tds[1].text #产品名称
            item.guwen = tds[2].text  #投资顾问

            title_a = tds[1].find('a')
            guwen_a = tds[2].find('a')
            if title_a:
                item.product_url = self.site + title_a['href']
            if guwen_a:
                item.guwen_url = self.site + guwen_a['href']

            item.date_jingzhi = tds[3].text #净值日期
            item.unit_jingzhi = tds[4].text #单位净值
            item.sum_jingzhi = tds[5].text # 累计净值
            item.sum_earn = tds[6].text #累计收益
            item.year_earn = tds[7].text #年化收益
            item.prechange = tds[8].text #净值变动

            print item
            items.append(item)

        item_dict = [item.__dict__ for item in items]
        df = pd.DataFrame(item_dict)
        # print df.head()
        df.to_sql('simu_jingzhi', engine, if_exists='append', index=False)
        print "success:"

if __name__ == "__main__":
    simu = Simuwang()
    simu.get_jingzhi()