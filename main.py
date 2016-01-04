#coding=utf8

from data_grab.xueqiu import XueQiu
from data_grab.weibo import Weibo
from data_grab.sina_licaishi import Licaishi
from util.helper import fn_timer

from multiprocessing.dummy import Pool as ThreadPool
import ConfigParser

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

    user_ids = cf.get('user_id', 'xueqiu').split(',')

    xueqiu = XueQiu()
    xueqiu_user_list = user_ids
    [xueqiu.get_user_activity_info(user_id) for user_id in xueqiu_user_list]

def run_weibo():

    user_ids = cf.get('user_id', 'weibo').split(',')

    weibo = Weibo()
    weibo_user_list = user_ids
    [weibo.get_weibo_list(user_id) for user_id in weibo_user_list]

def run_licaishi():

    user_ids = cf.get('user_id', 'licaishi').split(',')

    licaishi = Licaishi()
    licaishi_user_list = user_ids
    [licaishi.get_licaishi_viewpoint_list(user_id) for user_id in licaishi_user_list]


if __name__ == "__main__":
    refresh_web_in_real_time()