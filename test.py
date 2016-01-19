#coding=utf8

from data_preprocess.main_body import extract
from util.webHelper import get_requests

def test_extract_html():
    url = "http://maxomnis.iteye.com/blog/1998903"
    r = get_requests(url, has_proxy=False)
    t = extract(r.text)
    print t

test_extract_html()