# -*- coding:utf8 -*-

import os
import urllib
import time, datetime
import pexpect
import re

from bs4 import BeautifulSoup
from pandas import DataFrame

from util.CodeConvert import *



class IP_Proxy:
    def __init__(self):
        self.source = 'http://www.haodailiip.com/guonei/page'
        self.count = 5
        self.ip_items = []
        self.dir_path = '../Data/'


    def parse(self, url):
        try:
            page = urllib.urlopen(url)
            data =  page.read()
            soup = BeautifulSoup(data, "html5lib")
            print soup.get_text()
            body_data = soup.find('table', attrs={'class':'content_table'})
            res_list = body_data.find_all('tr')
            for res in res_list:
                each_data = res.find_all('td')
                if len(each_data) > 3 and not 'IP' in each_data[0].get_text() and '.' in each_data[0].get_text():
                    print each_data[0].get_text().strip(), each_data[1].get_text().strip()
                    item = IPItem()
                    item.ip = each_data[0].get_text().strip()
                    item.port = each_data[1].get_text().strip()
                    item.addr = each_data[2].get_text().strip()
                    item.tpye = each_data[3].get_text().strip()
                    self.ip_items.append(item)
        except Exception,e:
            print e


    def test_ip_speed(self):
        tmp_items = []
        for item in self.ip_items:

            (command_output, exitstatus) = pexpect.run("ping -c1 %s" % item.ip, timeout=5, withexitstatus=1)
            if exitstatus == 0:
                print command_output
                m = re.search("time=([\d\.]+)", command_output)
                if m:
                    print 'time=', m.group(1)
                    item.speed = float(m.group(1))
                    tmp_items.append(item)

        self.ip_items = tmp_items

    def save_data(self):
        df = DataFrame({'IP':[item.ip for item in self.ip_items],
                        'Port':[item.port for item in self.ip_items],
                        'Addr':[item.addr for item in self.ip_items],
                        'Type':[item.tpye for item in self.ip_items],
                        'Speed':[item.speed for item in self.ip_items]
                        }, columns=['IP', 'Port', 'Addr', 'Type', 'Speed'])
        print df[:10]
        df['Time'] = GetNowTime()
        df = df.sort_index(by='Speed')

        now_data = GetNowDate()


        file_name = self.dir_path +'ip_proxy_' + now_data + '.xlsx'

        df.to_excel(file_name)


    def run(self):
        for i in range(1, self.count+1):
            url = self.source.replace('page', str(i))
            self.parse(url)
            time.sleep(3)

        self.test_ip_speed()

        self.save_data()

class IPItem:
    def __init__(self):
        self.ip = ''    # IP
        self.port = ''  # Port
        self.addr = ''  # 位置
        self.tpye = ''  #类型:http; https
        self.speed = -1 #速度

if __name__ == "__main__":
    ip_proxy = IP_Proxy()
    ip_proxy.run()
