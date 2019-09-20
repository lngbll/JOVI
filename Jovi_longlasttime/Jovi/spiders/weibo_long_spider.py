import json
import logging
import os
import re
import sys

import redis
from lxml import etree
from requests import exceptions
from scrapy import Selector

sys.path.append(os.path.abspath(os.getcwd()))
from Jovi.settings import *
from Jovi.tools import weibo_login, bloomfilter

import time


class WeiBoLongSpider(object):

    def __init__(self):
        # self.date = datetime.datetime.now().strftime('%m%d')
        log_dir = os.path.join(os.path.split(__file__)[0], '..', '..', 'log', '微博长文')
        date = time.strftime('%Y-%m-%d', time.localtime())
        self.logger = logging.getLogger('微博长文')
        self.logger.setLevel(logging.ERROR)
        self.handler = logging.FileHandler(os.path.join(log_dir,'{}.log'.format(date)))
        self.formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

        os.chdir('e:')
        self.dir = 'e:\\微博长文'
        if os.path.exists(self.dir):
            os.chdir(self.dir)
        else:
            os.mkdir(self.dir)
            os.chdir(self.dir)
        self.r = redis.Redis(host='localhost', port=6379, db=1)
        self.bloomFilter = bloomfilter.BloomFilter(redis=self.r, capacity=BLOOM_CAPACITY, error_rate=BLOOM_ERROR_RATE,
                                                   redis_key='JOVI_ARTICLES')
        self.weibo_login = weibo_login.weibo_login()
        self.weibo_login.run()
        self.session = self.weibo_login.session
        self.channels = {
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
        print('redis开启')

    def start_requests(self, v, page):
        t = int(time.time() * 10000)
        page = page
        url = 'https://d.weibo.com/p/aj/discover/loading?ajwvr=6&id={}&uid=5234071528&page={}&__rnd={}'.format(v, page,
                                                                                                               t)
        return url

    def get_url(self, url):
        try:
            resp = self.session.get(url)
            DOM = self.json_to_dom(resp)
            urls = DOM.xpath('//ul[@class="pt_ul clearfix"]/li/@href')
            return urls
        except Exception as e:
            self.logger.exception(e)

    def json_to_dom(self, resp):
        try:
            data = json.loads(resp.text)
            html = data['data']['html']
            dom = etree.HTML(html)
            return dom
        except Exception as e:
            self.logger.exception(e)

    def get_content(self, url, k):
        global counter
        try:
            if 'https' in url:
                url = url
            else:
                url = 'https:' + url
            try:
                resp = self.session.get(url)
                resp.raise_for_status()
            except exceptions:
                return
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
            if self.bloomFilter.contains(title):
                print('重复>>%s' % title)
                return
            else:
                if len(content) > 50:
                    line = title + ',' + content + '\n'
                    with open(k + '.txt', 'a', encoding="utf-8") as file:
                        file.write(line)
                        print(title[:20] + '...')
                    counter[k] += 1
                    self.bloomFilter.add(title)
                else:
                    print('太短>>%s' % title)
        except Exception as e:
            self.logger.exception(e)

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
                            time.sleep(1)
                    except Exception:
                        self.logger.error('出现异常', exc_info=True)
                page += 1


if __name__ == '__main__':
    counter = dict()
    a = WeiBoLongSpider()
    a.main()
