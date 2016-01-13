#coding=utf8

from data_grab.xueqiu import XueQiu
from data_grab.weibo import Weibo
from data_grab.sina_licaishi import Licaishi
from util.helper import fn_timer

from multiprocessing.dummy import Pool as ThreadPool
import ConfigParser
import sys

cf = ConfigParser.ConfigParser()
cf.read('../config.ini')

# 实时刷新雪球
@fn_timer
def refresh_web_in_real_time():

    func_list = [run_weibo, run_licaishi,run_xueqiu] #run_weibo, run_licaishi,run_xueqiu,
    #多线程
    # pool = ThreadPool(processes=3)
    # pool.map(run, func_list)
    # pool.close()
    # pool.join()

    for func in func_list:
        run(func)

def run(func):
    func()

def run_xueqiu():
    try:
        user_ids = cf.get('user_id', 'xueqiu').split(',')

        xueqiu = XueQiu()
        xueqiu_user_list = user_ids
        [xueqiu.get_user_activity_info(user_id) for user_id in xueqiu_user_list]
    except Exception,e:
        print e

def run_weibo():
    try:
        user_ids = cf.get('user_id', 'weibo').split(',')

        weibo = Weibo()
        weibo_user_list = user_ids
        [weibo.get_weibo_list(user_id) for user_id in weibo_user_list]
    except Exception,e:
        print e

def run_licaishi():
    try:
        user_ids = cf.get('user_id', 'licaishi').split(',')

        licaishi = Licaishi()
        licaishi_user_list = user_ids
        [licaishi.get_licaishi_viewpoint_list(user_id) for user_id in licaishi_user_list]
    except Exception,e:
        print e

#### For XueQiu

def run_xueqiu_big_v():
    """
    获取雪球大V
    """

    xueqiu = XueQiu()
    xueqiu.run_get_big_v()

def run_xueqiu_big_v_article():
    """
    获取大V文章列表
    """
    xueqiu = XueQiu()
    xueqiu.get_publish_articles_by_id()


if __name__ == "__main__":

    if len(sys.argv) == 1:
        refresh_web_in_real_time()
    elif len(sys.argv) == 2 and sys.argv[1] == 'xueqiu':
        run_xueqiu_big_v()
    elif len(sys.argv) == 2 and sys.argv[1] == 'weibo':
        run_weibo()
    elif len(sys.argv) == 2 and sys.argv[1] == 'licaishi':
        run_licaishi()