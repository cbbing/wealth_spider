import web, datetime

from db_config import *
from main import cf

db = web.database(dbn='mysql', db=db_name_mysql, host=host_mysql, port=port_mysql, user=user_mysql, passwd=pwd_mysql)

#db = web.database(dbn='mysql', db='wealth_db', port=3307, user='root', passwd='root')

def get_posts_xueqiu():

    ids = cf.get('user_id', 'xueqiu').split(',')
    return db.select(mysql_table_xueqiu_article, where='user_id in ({0})'.format(','.join(ids)), order='publish_time DESC', limit=10)
    #return db.select('entries', order='id DESC')

def get_posts_weibo():
    ids = cf.get('user_id', 'weibo').split(',')
    return db.select(mysql_table_weibo_article, where='user_id in ({0})'.format(','.join(ids)), order='publish_time DESC', limit=10)
    #return db.select('entries', order='id DESC')

def get_posts_licaishi():
    ids = cf.get('user_id', 'licaishi').split(',')
    return db.select(mysql_table_licaishi_viewpoint, where='user_id in ({0})'.format(','.join(ids)), order='publish_time DESC', limit=10)
    #return db.select('entries', order='id DESC')

def get_post(id):
    try:
        return db.select('entries', where='id=$id', vars=locals())[0]
    except IndexError:
        return None

def new_post(title, text):
    db.insert('entries', title=title, content=text, posted_on=datetime.datetime.utcnow())

def del_post(id):
    db.delete('entries', where="id=$id", vars=locals())

def update_post(id, title, text):
    db.update('entries', where="id=$id", vars=locals(),
        title=title, content=text)