#coding=utf8

from data_preprocess.main_body import extract
from util.webHelper import get_requests

def test_extract_html():
    url = "http://maxomnis.iteye.com/blog/1998903"
    r = get_requests(url, has_proxy=False)
    t = extract(r.text)
    print t

#test_extract_html()

import pandas as pd

# filename = 'pima-indians-diabetes.data.csv'
# df = pd.read_csv(filename, header=None)
# print df.head()
# df0 = df[df[8]==0]
# df1 = df[df[8]==1]
# print len(df), len(df0), len(df1)

from selenium import webdriver
from bs4 import BeautifulSoup as bs
driver = webdriver.Firefox()
#'http://blog.sina.com.cn/lm/iframe/top100/153.html') #'http://blog.sina.com.cn/lm/top/rank/')
driver.get('http://blog.eastmoney.com/caijing.html')
print driver.page_source
soup = bs(driver.page_source, 'html5lib')
#td_all = soup.find_all('td', {'class':'link335bbd'}) # sina_blog
td_all = soup.find_all('li', {'class':'w20_1'}) # sina_blog

datas = []
for td in td_all:
    a = td.find('a')
    if a:
        title = a.text
        href = a['href']
        datas.append((title, href))
print len(datas)
df = pd.DataFrame(datas, columns=['title', 'href'])
df.to_excel('Data/sina_blog.xlsx', index=False)
df.to_csv('Data/sina_blog.csv', index=False)
driver.quit()