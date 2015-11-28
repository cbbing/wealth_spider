# -*- coding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
import urllib
import time, datetime
import pexpect
import platform
import re
import pandas as pd

from bs4 import BeautifulSoup
from pandas import DataFrame
from subprocess import *
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool


from util.CodeConvert import *
from util.helper import *



class IP_Proxy:
    def __init__(self):
        self.source = 'http://www.haodailiip.com/guonei/page'
        self.count = 10
        self.ip_items = []
        self.dir_path = '../Data/'


    def parse(self, url):
        try:
            page = urllib.urlopen(url)
            data =  page.read()
            soup = BeautifulSoup(data, "html5lib")
            #print soup.get_text()
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
                    item.type = each_data[3].get_text().strip()
                    if item.type.lower() == "http" or item.type.lower() == "https":
                        self.ip_items.append(item)
        except Exception,e:
            print e


    def test_ip_speed(self):

        # t0l = time.time()
        # pooll = Pool(processes=20)
        # for item in self.ip_items:
        #     pooll.apply(self.ping_one_ip, args=(item.ip,))
        # #pooll.map(self.ping_one_ip, self.ip_items)
        # pooll.close()
        # pooll.join

        t0 = time.time()

        #多线程
        pool = ThreadPool(processes=20)
        pool.map(self.ping_one_ip, range(len(self.ip_items)))
        pool.close()
        pool.join()

        t1 = time.time()
        #print "Total time running multi: %s seconds" % ( str(t0-t0l))
        print "Total time running multi: %s seconds" % ( str(t1-t0))

        #单线程
        # for index in range(len(self.ip_items)):
        #     self.ping_one_ip(index)
        # t2 = time.time()
        # print "Total time running multi: %s seconds" % ( str(t1-t0))
        # print "Total time running single: %s seconds" % ( str(t2-t1))

        print len(self.ip_items)
        self.ip_items = [item for item in self.ip_items if item.speed >=0 and item.speed < 1500.0]    # 超时1.5s以内
        print len(self.ip_items)




    def ping_one_ip(self, index):
        systemName = platform.system()
        if systemName == 'Windows':
            #p = Popen(["ping.exe",item.ip], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
            p = Popen("ping.exe %s -n 1" % (self.ip_items[index].ip), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
            out = p.stdout.read().decode('gbk').encode('utf8')

            m = re.search(u'=(\d+)ms', out)
            if m:
                print self.ip_items[index].ip, ' time=',m.group(1),'ms'
                self.ip_items[index].speed = float(m.group(1))
            else:
                print self.ip_items[index].ip, ' time out'

        else:
            (command_output, exitstatus) = pexpect.run("ping -c1 %s" % self.ip_items[index].ip, timeout=5, withexitstatus=1)
            if exitstatus == 0:
                print command_output
                m = re.search("time=([\d\.]+)", command_output)
                if m:
                    print  self.ip_items[index].ip, ' time=', m.group(1),'ms'
                    self.ip_items[index].speed = float(m.group(1))
                else:
                    print self.ip_items[index].ip, ' time out'

    def save_data(self):
        df = DataFrame({'IP':[item.ip for item in self.ip_items],
                        'Port':[item.port for item in self.ip_items],
                       # 'Addr':[item.addr for item in self.ip_items],
                        'Type':[item.type for item in self.ip_items],
                        'Speed':[item.speed for item in self.ip_items]
                        }, columns=['IP', 'Port', 'Type', 'Speed'])

        df['Time'] = GetNowTime()

        #df = df.applymap(lambda x : encode_wrap(x))
        print df[:10]

        df = df.sort_index(by='Speed')

        now_data = GetNowDate()

        file_name = self.dir_path +'ip_proxy_' + now_data

        df.to_csv(file_name + '.csv')
        #df.to_excel( 'ip.xlsx', index=False)

        # writer = pd.ExcelWriter(file_name+'.xlsx')
        # df.to_excel(writer,'Sheet1')
        # writer.save()

    @fn_timer
    def run(self):
        for i in range(1, self.count+1):
            url = self.source.replace('page', str(i))
            self.parse(url)
            if (i < self.count+1):
                print 'next page:', i+1
                time.sleep(3)

        print 'test speed begin...'
        self.test_ip_speed()
        print 'test speed end'

        self.save_data()

class IPItem:
    def __init__(self):
        self.ip = ''    # IP
        self.port = ''  # Port
        self.addr = ''  # 位置
        self.type = ''  #类型:http; https
        self.speed = -1 #速度

if __name__ == "__main__":
    ip_proxy = IP_Proxy()
    ip_proxy.run()
