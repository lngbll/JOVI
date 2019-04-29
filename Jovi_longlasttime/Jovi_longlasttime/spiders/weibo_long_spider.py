import json
import os
import random
import re
import time
from hashlib import sha1

import redis
import requests
from lxml import etree
from scrapy import Selector


class WeiBoLongSpider(object):
    channels = {
        '军事': '623751_4',
        '宠物': '623751_10008',
        '汽车': '623751_10',
        '体育': '623751_3',
        '财经': '623751_6',
        '科技': '623751_5',
        '美食': '623751_10012',
        '育儿': '623751_10004',
        '动漫': '623751_10005',
        '历史': '623751_10013',
        '游戏': '623751_10014',
        '运动健身': '623751_10009',
        '房产': '623751_9'
    }
    cookies = 'SINAGLOBAL=5410448660622.509.1543482216551; UOR=,,www.google.com; login_sid_t=47d185285b2a6490a92f0a254f648b7e; cross_origin_proto=SSL; _s_tentry=login.sina.com.cn; Apache=6214196438832.615.1556349541799; ULV=1556349541803:45:8:2:6214196438832.615.1556349541799:1555905085653; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhTFGMYuXqMc8ZBnmZuAPaL5JpX5o275NHD95QfeoeXehMpSKzRWs4Dqcj_i--ci-zfiK.Xi--4iK.Ri-z0i--fiKysi-2Xi--4iKn0i-2pi--Xi-iWi-iW; SSOLoginState=1556349571; wvr=6; ALF=1587885601; SCF=AlGGDSpqLT23LmME-_qggKJQFn10ABSHFSJKq8tyoLAXEIjEZ-XuNF8SbCuTRqkgdKlen17Qihz2zkw1zHHI8fY.; SUB=_2A25xwHLyDeRhGeNM6FYR9y_JyTSIHXVStOM6rDV8PUNbmtAKLXTjkW9NTj-aGj4bcq6bY7BOI16uOmd2vY_6lPF0; SUHB=0N2Fzod6R1zlF9; wb_view_log_5234071528=1920*10801; YF-Page-G0=aabeaa17d9557111c805fb15a9959531|1556349622|1556349608'
    headers1 = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': cookies,
        'Host': 'd.weibo.com',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
    }
    headers2 = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': cookies,
        'Host': 'weibo.com',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'
    }

    def __init__(self):
        # self.date = datetime.datetime.now().strftime('%m%d')
        os.chdir('e:')
        self.dir = 'e:\\微博长文'
        if os.path.exists(self.dir):
            os.chdir(self.dir)
        else:
            os.mkdir(self.dir)
            os.chdir(self.dir)
        self.r = redis.Redis(host='localhost', port=6379, db=1)
        print('redis开启')

    def start_requests(self, v, page):
        t = int(time.time() * 10000)
        page = page
        url = 'https://d.weibo.com/p/aj/discover/loading?ajwvr=6&id={}&uid=5234071528&page={}&__rnd={}'.format(v, page, t)
        return url

    def get_url(self, url):
        try:
            resp = requests.get(url, headers=self.headers1)
            DOM = self.json_to_dom(resp)
            urls = DOM.xpath('//ul[@class="pt_ul clearfix"]/li/@href')
            return urls
        except Exception as e:
            print('出现异常%s' % url)
            print(e)

    def json_to_dom(self, resp):
        try:
            data = json.loads(resp.text)
            html = data['data']['html']
            dom = etree.HTML(html)
            return dom
        except Exception as e:
            print('出现异常')
            print(e)

    def get_content(self, url, k):
        global counter
        try:
            if 'https' in url:
                url = url
            else:
                url = 'https:' + url
            resp = requests.get(url, headers=self.headers2)
            resp = resp
            selector = Selector(resp)
            contents = selector.xpath('//div[@class="WB_editor_iframe_new"]/p//text()').extract()
            pattern = r'点击[上下]方|关注(.*?)公众号|关注(.*?)微信|↓|原文|相关阅读|原文|说明：|原标题|原题|选自：|' \
                      r'公众号|▲|文章来自|本文|｜|来自网络|作者：|声明：|译自|如有侵权|\||编辑|编者|往期回顾|记者|' \
                      r'点击进入|提示：|导语：|转载联系|责编|译者：|来源：| document.write'
            content = ''
            for i in contents:
                if re.search(pattern, i):
                    continue
                else:
                    content += i.strip()
            content = content.replace('\xa0', '').replace('\u3000', '').replace('\r', '').replace('\n', '') \
                .replace('\t', '')
            title = selector.xpath('//div[@class="title"]/text()').extract_first().strip()
            s1 = sha1(title.encode('utf-8'))
            fp = s1.hexdigest()
            if self.r.sismember('article_title_fp_new', fp):
                print('重复>>%s' % title)
                return
            else:
                if len(content) > 50:
                    line = title + ',' + content + '\n'
                    with open(k + '.txt', 'a', encoding="utf-8") as file:
                        file.write(line)
                        print(title[:20] + '...')
                    counter[k] += 1
                    self.r.sadd('article_title_fp_new', fp)
                else:
                    print('太短>>%s' % title)
        except Exception as e:
            print('异常 :%s' % e)

    def main(self):
        global counter
        for k, v in self.channels.items():
            counter[k] = 0
            page = 1
            while True:
                url = self.start_requests(v, page)
                urls = self.get_url(url)
                print('-' * 30 + '%s第%d页' % (k, page))
                url_list = urls
                if url_list == []:
                    break
                else:
                    try:
                        for i in urls:
                            self.get_content(i, k)
                            time.sleep(0.5 * random.random())
                    except Exception as e:
                        print(e)
                page += 1
        # count = 0
        # with open('统计.txt', 'w', encoding='utf-8') as c:
        #     for i in counter.keys():
        #         count += counter[i]
        #         c.write('%s:%d' % (i, counter[i]))
        #     c.write('总数:%s' % count)


if __name__ == '__main__':
    counter = dict()
    a = WeiBoLongSpider()
    a.main()