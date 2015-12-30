#coding=utf8

from data_grab.xueqiu import XueQiu
from data_grab.weibo import Weibo
from data_grab.sina_licaishi import Licaishi

# 实时刷新雪球
def refresh_web_in_real_time():
    xueqiu = XueQiu()
    xueqiu_user_list = ['3037882447']
    [xueqiu.get_user_activity_info(user_id) for user_id in xueqiu_user_list]

    weibo = Weibo()
    weibo_user_list = ['2144596567']
    [weibo.get_weibo_list(user_id) for user_id in weibo_user_list]

    licaishi = Licaishi()
    licaishi_user_list = ['2357529875']
    [licaishi.get_licaishi_viewpoint_list(user_id) for user_id in licaishi_user_list]


if __name__ == "__main__":
    refresh_web_in_real_time()