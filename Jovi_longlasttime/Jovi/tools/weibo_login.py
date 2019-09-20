'''
    2019.9.3 tsy
    微博登录以rsa加密，参考'https://www.cnblogs.com/mouse-coder/archive/2013/03/03/2941265.html'，并修正了部分
    登录控件为一个js文件
    一共有三步：
    分别为prelogin,login,crossdomain,final_requests
    之前用的是requests.cookie.RequestCookieJar().update来保存更新cookies,发现登录成功之后总是无法使用里面的cookie来爬微博,索性
    直接用requests.session,无需考虑cookie,只要登录成功就可以直接使用此session来爬虫，厉害了requests.session
'''

import binascii
import json
import logging
import re
import time
from base64 import b64encode

import requests
import rsa
from requests.cookies import RequestsCookieJar


class weibo_login(object):
    def __init__(self):
        self.cookies = RequestsCookieJar()
        self.pre_login_info = None
        self.sp = None
        self.username = 13760398874
        self.pwd = 'Yangfei123@'
        self.rsa2_password = None

        self.session = requests.session()
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
        }
        self.prelt = 0

    def gen_rsa_sp(self):
        rsapubkey = int(self.pre_login_info.get('pubkey'), 16)
        key = rsa.PublicKey(rsapubkey, 65537)
        message = '{}\t{}\n{}'.format(self.pre_login_info.get('servertime'), self.pre_login_info.get('nonce'),
                                      self.pwd).encode()
        password = rsa.encrypt(message, key)
        self.rsa2_password = binascii.b2a_hex(password)
        return self.rsa2_password

    def login(self):
        url1 = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        # url1 = 'https://login.sina.com.cn/signup/signin.php'
        data = {
            'su': b64encode(b'13760398874'),
            'entry': 'weibo',
            'geteway': 1,
            'from': None,
            'savestate': 7,
            'qrcode_flag': False,
            'useticket': 1,
            'pagerefer': 'https://login.sina.com.cn/crossdomain2.php?action=login&r=https%3A%2F%2Fpassport.weibo.com%2Fwbsso%2Flogout%3Fr%3Dhttps%253A%252F%252Fweibo.com%26returntype%3D1',
            'vsnf': 1,
            'service': 'miniblog',
            'servertime': time.time(),
            'nonce': self.pre_login_info.get('nonce'),
            'pwencode': 'rsa2',
            'rsakv': self.pre_login_info.get('rsakv'),
            'sp': self.gen_rsa_sp(),
            'sr': '1920*1080',
            'encoding': 'UTF-8',
            'prelt': self.prelt,
            'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        r1 = self.session.post(url1, data=data, timeout=10)
        r1.raise_for_status()
        self.cookies.update(r1.cookies)
        try:
            url2 = re.search(r'location.replace\("(.*?)"\);', r1.content.decode('gbk'), re.S).group(1)
            r2 = self.session.get(url=url2, timeout=10)
            r2.raise_for_status()
            self.cookies.update(r2.cookies)
            url3 = re.search(r'location.replace\(\'(.*?)\'\);', r2.content.decode('gbk'), re.S).group(1)
            r2 = self.session.get(url=url3, timeout=10)
            r2.raise_for_status()
            self.cookies = self.session.cookies
        except Exception as e:
            logging.exception(e)

    def pre_login(self):
        try:
            pre_login_time = int(1000 * time.time())
            r = self.session.get(
                'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.19)&_=1567405550547')
            r.raise_for_status()
            d = json.loads(r.text.lstrip('sinaSSOController.preloginCallBack(').rstrip(')'))
            self.pre_login_info = d
            self.prelt = int(1000 * time.time()) - pre_login_time - d.get('exectime')
        except Exception as e:
            logging.exception(e)

    def logout(self):
        try:
            r = self.session.get('https://login.sina.com.cn/sso/logout.php?entry=miniblog&r=https%3A%2F%2Fweibo.com',
                                 timeout=10)
            r.raise_for_status()
            self.cookies.update(r.cookies)
        except Exception as e:
            logging.exception(e)

    def init_cookie(self):
        try:
            r = self.session.get('https://weibo.com')
            r.raise_for_status()
        except Exception as e:
            logging.exception(e)

    def run(self):
        self.init_cookie()
        self.pre_login()
        self.login()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()


if __name__ == '__main__':
    w = weibo_login()
    w.run()
