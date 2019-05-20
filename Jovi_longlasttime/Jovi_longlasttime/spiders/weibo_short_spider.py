import codecs
import datetime
import json
import os
import random
import re
import time
from hashlib import sha1

import redis
import requests
from scrapy import Selector
import time,logging

class weibo_short_spider(object):
    def __init__(self):
        log_dir = 'e:\\日志文件夹\\JOVI新闻爬虫\\weibo_short_spider'
        date = time.strftime('%Y-%m-%d', time.localtime())
        self.logger = logging.getLogger('weibo_long_spider')
        self.logger.setLevel(logging.ERROR)
        self.handler = logging.FileHandler('{}\\{}.log'.format(log_dir, date))
        self.formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        self.cookies = 'SINAGLOBAL=5410448660622.509.1543482216551; wvr=6; login_sid_t=15eabedbe3d504ba094583fb48f2a12e; cross_origin_proto=SSL; _s_tentry=login.sina.com.cn; UOR=,,www.google.com; Apache=5026532364951.99.1558343298769; ULV=1558343298776:55:8:1:5026532364951.99.1558343298769:1558166820902; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhTFGMYuXqMc8ZBnmZuAPaL5JpX5o275NHD95QfeoeXehMpSKzRWs4Dqcj_i--ci-zfiK.Xi--4iK.Ri-z0i--fiKysi-2Xi--4iKn0i-2pi--Xi-iWi-iW; ALF=1589879332; SSOLoginState=1558343332; SCF=AlGGDSpqLT23LmME-_qggKJQFn10ABSHFSJKq8tyoLAX1QMaf2aQIUm_KCfWJKsxB9hZIPq0tnj5XzIrRBgRoVQ.; SUB=_2A25x5h71DeRhGeNM6FYR9y_JyTSIHXVSknc9rDV8PUNbmtBeLXHEkW9NTj-aGitTlGeaAeJ-KHtncDuSoo3tEzFO; SUHB=0P180dM8OThHW1; wb_view_log_5234071528=1920*10801; webim_unReadCount=%7B%22time%22%3A1558343404682%2C%22dm_pub_total%22%3A0%2C%22chat_group_pc%22%3A0%2C%22allcountNum%22%3A0%2C%22msgbox%22%3A0%7D; YF-Page-G0=237c624133c0bee3e8a0a5d9466b74eb|1558343416|1558343389'
        self.head1 = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': self.cookies,
            'Host': 'd.weibo.com',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent ': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'
        }
        self.head2 = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': self.cookies,
            'Host': 'd.weibo.com',
            'Pragma': 'no-cache',
            'Referer': 'https://d.weibo.com/102803_ctg1_6288_-_ctg1_6288?from=faxian_hot&mod=fenlei',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent ': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'
        }
        self.head3 = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': self.cookies,
            'Host': 'd.weibo.com',
            'Pragma': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
            'X-Requested-With ': 'XMLHttpRequest'
        }

    def get_channels(self, url):
        resp = requests.get(url, headers=self.head1)
        data = re.search(r'"html":"<div class=\\"WB_cardwrap S_bg2\\">(.*?)<\\/div>\\n"}\)</script>', resp.text).group(
            1)
        html = codecs.escape_decode(bytes(data, 'utf-8'))[0].decode('utf-8')
        channels = re.findall(r'<li class="li_text">(.*?)<\\/li>', html, re.S)
        c = dict()
        for i in channels[2:]:
            url = re.search(r'href="\\(.*?)" bpfilter', i).group(1)
            k = re.search(r'<span class="text width_fix W_autocut">(.*?)<\\/span', i, re.S).group(1).strip()
            id = re.search(r'/(.*?)\?', url).group(1)
            print(k, id)
            # yield scrapy.Request(url='https://d.weibo.com' + url, callback=self.get_text, meta=meta,
            #                      headers=self.header2)
            c[k] = id
        return c

    def get_urls(self, html):
        unfold = Selector(text=html).xpath('//a[@class="WB_text_opt"]/@action-data').extract()
        urls = []
        for i in unfold:
            url = 'https://d.weibo.com/p/aj/mblog/getlongtext?ajwvr=6&{}&__rnd={}'.format(i, int(time.time() * 1000))
            urls.append(url)
        print('-------------------------------------------------------')
        return urls

    def get_page(self, page, v):
        circle = page % 6
        page_bar = circle - 1
        current_page = page
        pre_page = (page - 1) // 6
        page = page // 6
        _rnd = int(time.time() * 10000)
        pid = 'Pl_Core_NewMixFeed__3'
        id = v
        if circle:
            pattern = 'https://d.weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain={}' \
                      '&from=faxian_hot&mod=fenlei&pagebar={}&tab=home&current_page=' \
                      '{}&pre_page={}&page={}&pl_name={}&id={}&script_uri' \
                      '=/{}&feed_type=1&domain_op={}&__rnd={}'.format(id, page_bar, current_page, pre_page, page, pid,
                                                                      id, id, id, _rnd)
        else:
            pattern = 'https://d.weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain={}&from=faxian_hot&mod=fenlei' \
                      '&pre_page={}&page={}&pids={}&current_page={}&since_id=' \
                      '&pl_name={}&id={}&script_uri=/{}&feed_type=1&domain_op={}&__rnd={}'.format(id, pre_page, page,
                                                                                                  pid, current_page,
                                                                                                  pid, id, id, id, _rnd)
        url = pattern
        return url

    def get_content(self, url, k, r):
        global counter
        time.sleep(random.random())
        try:
            resp = requests.get(url, headers=self.head3)
            data = json.loads(resp.text)
            html = data['data']['html']
            html = '<body>{}</body>'.format(html)
            contents = Selector(text=html, type='html').xpath('//body/text()').extract()
            pattern = r'来源|关注(.*?)公众号|关注(.*?)微信|原文|选自|公众号|来自|作者：|声明：|如有侵权|编辑|编者|记者|点击进入|提示：|转载联系|编辑|来源|图自|图源|报导'
            content = ''
            for i in contents:
                if re.search(pattern, i):
                    continue
                else:
                    content += i.strip()
            content = content.replace('\xa0', '').replace('\u3000', '').replace('\r', '').replace('\n', '').replace(
                '\t', '')
            s1 = sha1(content.encode('utf-8'))
            fp = s1.hexdigest()
            if r.sismember('short_blog', fp):
                print('重复>>%s' % (content[:11] + '...'))
                return
            else:
                if len(content) > 50:
                    line = content + '\n'
                    with open(k + '.txt', 'a', encoding="utf-8") as file:
                        file.write(line)
                    counter[k] += 1
                    r.sadd('short_blog', fp)
                    print(content[:11] + '...')
                else:
                    print('太短>>%s' % (content[:11] + '...'))
        except Exception as e:
            self.logger.error('出现异常 %s'%url,exc_info=True)

    def main(self, url):
        os.chdir('e:')
        # now = datetime.datetime.now()
        # date = now.strftime('%m%d')
        if not os.path.exists('e:\微博短文'):
            os.mkdir('e:\微博短文')
        os.chdir('e:\微博短文')
        r = redis.Redis(host='localhost', port=6379, db=1)
        print('redis开启')
        channels = self.get_channels(url)
        for k, v in channels.items():
            counter[k] = 0
            page = 1
            html = ''
            while '话题page页面返回为空时' not in html:
                try:
                    page_url = self.get_page(page, v)
                    res = requests.get(page_url, headers=self.head2)
                    data = json.loads(res.text)
                    html = data['data']
                    urls = self.get_urls(html)
                    for i in urls:
                        self.get_content(i, k, r)
                    page += 1
                except Exception:
                    logging.error('ip被禁',exc_info=True)
                    print('被禁IP,等待10分钟......')



if __name__ == '__main__':
    counter = dict()
    url = 'https://d.weibo.com/?topnav=1&mod=logo&wvr=6'
    a = weibo_short_spider()
    a.main(url)

