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


class weibo_short_spider(object):
    def __init__(self):
        self.cookies = 'SINAGLOBAL=5410448660622.509.1543482216551; UOR=,,www.google.com; login_sid_t=47d185285b2a6490a92f0a254f648b7e; cross_origin_proto=SSL; _s_tentry=login.sina.com.cn; Apache=6214196438832.615.1556349541799; ULV=1556349541803:45:8:2:6214196438832.615.1556349541799:1555905085653; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhTFGMYuXqMc8ZBnmZuAPaL5JpX5o275NHD95QfeoeXehMpSKzRWs4Dqcj_i--ci-zfiK.Xi--4iK.Ri-z0i--fiKysi-2Xi--4iKn0i-2pi--Xi-iWi-iW; SSOLoginState=1556349571; wvr=6; ALF=1587885601; SCF=AlGGDSpqLT23LmME-_qggKJQFn10ABSHFSJKq8tyoLAXEIjEZ-XuNF8SbCuTRqkgdKlen17Qihz2zkw1zHHI8fY.; SUB=_2A25xwHLyDeRhGeNM6FYR9y_JyTSIHXVStOM6rDV8PUNbmtAKLXTjkW9NTj-aGj4bcq6bY7BOI16uOmd2vY_6lPF0; SUHB=0N2Fzod6R1zlF9; wb_view_log_5234071528=1920*10801; webim_unReadCount=%7B%22time%22%3A1556349684806%2C%22dm_pub_total%22%3A0%2C%22chat_group_pc%22%3A0%2C%22allcountNum%22%3A0%2C%22msgbox%22%3A0%7D; YF-Page-G0=aabeaa17d9557111c805fb15a9959531|1556349707|1556349608'
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
            print('异常  %s' % url)
            print(e)

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
                    time.sleep(600)
                    print('被禁IP,等待10分钟......')
        # count = 0
        # with open('统计.txt', 'w', encoding='utf-8') as c:
        #     for i in counter.keys():
        #         count += counter[i]
        #         c.write('%s:%d\n' % (i, counter[i]))
        #     c.write('总数：%s' % count)


if __name__ == '__main__':
    counter = dict()
    url = 'https://d.weibo.com/?topnav=1&mod=logo&wvr=6'
    a = weibo_short_spider()
    a.main(url)
    # a.get_page(1000,'102803_ctg1_6788_-_ctg1_6788')
