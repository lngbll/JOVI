# -*- coding: utf-8 -*-
import json
import os
import time

import scrapy
from scrapy.selector import Selector

from Jovi.items import JoviLonglasttimeItem


class YidianAppSpider(scrapy.Spider):
    name = 'yidian_app'
    log_dir = os.path.join(os.path.split(__file__)[0], '..', '..', 'log', '一点资讯')
    date = time.strftime('%Y-%m-%d', time.localtime())
    start_urls = [
        'http://124.243.238.66/Website/channel/set-order?platform=1&appid=yidian&cv=3.4.2&version=010918&net=wifi']  # 游客模式登陆
    headers = {
        'User-Agent': 'Dalvik/1.6.0 (Linux; U; Android 4.4.2; SM-G955N Build/NRD90M)',
        'Host': '124.243.238.66',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Cookie': 'JSESSIONID=u4uOLPjqh3pdOcnGjcWkHQ'
    }
    cookies = {'JSESSIONID': 'u4uOLPjqh3pdOcnGjcWkHQ'}
    custom_settings = {
        'LOG_FILE': os.path.join(log_dir, '{}.log'.format(date)),
        'ITEM_PIPELINES': {
            'Jovi.pipelines.BloomFilterPipeline': 200,
            'Jovi.pipelines.Duppipline': 300,
            # # 'Jovi.pipelines.Mongopipline': 400,   #默认不开启MongoDB,节省内存资源
            'Jovi.pipelines.To_csv1': 500
        },
    }

    def start_requests(self):
        url = 'http://124.243.238.66/Website/user/get-info?platform=1&appid=yidian&cv=3.4.2&version=010918&net=wifi'
        yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, cookies=self.cookies)

    def parse(self, response):
        meta = dict()
        jr = json.loads(response.text)
        channels = jr['user_channels']
        for channel in channels:
            if channel['type'] == 'category':
                meta['second_tag'] = channel['name']
                for i in range(50):
                    url = 'http://124.243.238.66/Website/channel/news-list-for-channel?' \
                          'platform=1&infinite=true&cstart={}&cend={}&appid=yidian&cv=3.4.2' \
                          '&refresh=1&channel_id={}&fields=docid&fields=date&' \
                          'fields=image&fields=image_urls&fields=like&fields=source&' \
                          'fields=title&fields=url&fields=comment_count&fields=up&fields=down' \
                          '&version=010918&net=wifi'.format(30 * i, 30 * i + 30, channel['channel_id'])
                    yield scrapy.Request(url, meta=meta, callback=self.get_article, headers=self.headers,
                                         cookies=self.cookies, dont_filter=True)

    def get_article(self, response):
        meta = response.meta
        jr = json.loads(response.text)
        for i in jr['result']:
            docID = i.get('docid')
            if docID:
                url = 'http://124.243.238.66/Website/contents/content?' \
                      'platform=1&appid=yidian&related_docs=true&bottom_channels=true&docid={}' \
                      '&cv=3.4.2&related_wemedia=true&version=010918&net=wifi'.format(docID)
                yield scrapy.Request(url, meta=meta, callback=self.get_content, cookies=self.cookies, dont_filter=True)

    def get_content(self, response):
        meta = response.meta
        jr = json.loads(response.text)
        item = JoviLonglasttimeItem()
        item['first_tag'] = '一点资讯'
        item['second_tag'] = meta['second_tag']
        item['article_url'] = response.url
        item['article_title'] = jr['documents'][0]['title']
        try:
            s = Selector(text=jr['documents'][0]['content'])
        except:
            return
        ps = s.xpath('//p[not(@class)]//text()').getall()
        content = ''.join(map((lambda x: x.strip()), ps))
        item['article_content'] = content
        yield item
