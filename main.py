#coding=utf8

from data_grab.xueqiu import XueQiu

# 实时刷新雪球
def refresh_web_in_real_time():
    xueqiu = XueQiu()
    user_list = ['3037882447']

    [xueqiu.get_user_activity_info(user_id) for user_id in user_list]


if __name__ == "__main__":
    refresh_web_in_real_time()