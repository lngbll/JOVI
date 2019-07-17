#!coding=utf-8
import json
import re

import redis
import requests


import execjs
import execjs.runtime_names


class toutiao(object):
    def __init__(self, url):
        self.url = url
        self.s = requests.session()
        headers = {'Accept': '*/*',
                   'Accept-Language': 'zh-CN',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko',
                   'Connection': 'Keep-Alive',

                   }
        self.s.headers.update(headers)
        self.channel = re.search('ch/(.*?)/', url).group(1)

    def closes(self):
        self.s.close()

    def getdata(self):  # 获取数据
        headers = {'referer': self.url}
        max_behot_time = '0'
        self.s.headers.update(headers)
        source_url = []
        for _ in range(0, 50):  ##获取页数
            Honey = json.loads(self.get_js())
            eas = Honey['as']
            ecp = Honey['cp']
            signature = Honey['_signature']
            url = 'https://www.toutiao.com/api/pc/feed/?category={}&utm_source=toutiao&widen=1&max_behot_time={}&max_behot_time_tmp={}&tadrequire=true&as={}&cp={}&_signature={}'.format(
                self.channel, max_behot_time, max_behot_time, eas, ecp, signature)

            while True:
                req = self.s.get(url=url, verify=False)
                j = json.loads(req.text)
                data = j['data']
                if data!=[]:
                    break
            for k in range(0, 10):
                try:
                    source = 'https://www.toutiao.com/a' + j['data'][k]['group_id']
                    print(source)
                except:
                    print('返回为空')
                    source = ''
                source_url.append(source)  ##文章链接
        return source_url

    def get_js(self):
        f = open(r"E:\JOVI\Jovi_longlasttime\Jovi_longlasttime\signature.js", 'r', encoding='UTF-8')
        htmlstr = f.read()
        ctx = execjs.compile(htmlstr)
        return ctx.call('get_as_cp_signature')


if __name__ == '__main__':
    r = redis.Redis(host='localhost', port=6379, db=1)
    res = requests.get('https://s3a.pstatp.com/toutiao/resource/ntoutiao_web/page/home/whome/home_e14d2a0.js', )
    nav_item = re.search(r'navItem:(\[.*?\])', res.content.decode('utf-8'), re.S).group(1).replace(',url',
                                                                                                   ',\"url\"').replace(
        'name', '\"name\"').replace(',en', ',\"en\"')
    nav_more = re.search(r'navMore:(\[.*?\])', res.content.decode('utf-8'), re.S).group(1).replace(',url',
                                                                                                   ',\"url\"').replace(
        'name', '\"name\"').replace(',en', ',\"en\"')
    nav = json.loads(nav_item) + json.loads(nav_more)
    for i in nav[5:]:
        url = 'https://www.toutiao.com' + i['url']
        tt = toutiao(url)
        t = tt.getdata()
        tt.closes()
        for j in t:
            r.sadd('toutiao', j)

