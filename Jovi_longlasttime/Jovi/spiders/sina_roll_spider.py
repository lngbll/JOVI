# -*- coding: utf-8 -*-
import json
import re

import scrapy

from Jovi.items import JoviLonglasttimeItem


class XinaRollSpiderSpider(scrapy.Spider):
    name = 'sina_roll_spider'
    pid = '153'
    col = [
        {
            'name': "全部",
            'lid': "2509",
            'page': 9669
        },
        {
            'name': "国内",
            'lid': "2510",
            'page': 14550

        },
        {
            'name': "国际",
            'lid': "2511",
            'page': 488

        },
        {
            'name': "社会",
            'lid': "2669",
            'page': 597
        },
        {
            'name': "体育",
            'lid': "2512",
            'page': 4215
        },
        {
            'name': "娱乐",
            'lid': "2513",
            'page': 1212
        },
        {
            'name': "军事",
            'lid': "2514",
            'page': 1156

        },
        {
            'name': "科技",
            'lid': "2515",
            'page': 2148
        },
        {
            'name': "财经",
            'lid': "2516",
            'page': 6529
        },
        {
            'name': "股市",
            'lid': "2517",
            'page': 3507
        },
        {
            'name': "美股",
            'lid': "2518",
            'page': 12854
        }
    ]
    meta = dict()

    def start_requests(self):
        meta = self.meta
        for i in self.col:
            meta['third_tag'] = i['name']
            for j in range(1, i['page'] + 1):
                url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid={}&k=&num=50&page={}'.format(i['lid'],
                                                                                                             j)
                yield scrapy.Request(url, meta=meta, callback=self.get_urls)

    def get_urls(self, response):
        meta = response.meta
        data = json.loads(response.text)
        for i in data['result']['data']:
            url = i['url']
            meta['title'] = i['title']
            yield scrapy.Request(url, callback=self.get_content, meta=meta)

    def get_content(self, response):
        item = JoviLonglasttimeItem()
        meta = response.meta
        article = response.xpath('//div[@class="article"]/p[not(@class)]//text()').extract()
        content = ''
        pattern = r'原标题：|特别声明：|{}'.format(meta['title'])
        for i in article:
            if re.search(pattern, i):
                continue
            else:
                content += i.strip()
        item['article_content'] = content
        item['article_title'] = meta['title']
        item['article_url'] = response.url
        item['first_tag'] = '新浪滚动'
        item['second_tag'] = '新浪滚动'
        item['third_tag'] = meta['third_tag']
        yield item
