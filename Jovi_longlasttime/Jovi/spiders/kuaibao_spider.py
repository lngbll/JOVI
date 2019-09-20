# -*- coding: utf-8 -*-
import json
import re

import scrapy

from Jovi.items import JoviLonglasttimeItem

"""
    天天快报网页版spider,接口无须登录信息cookies，需要参数p(页码),channel(频道),没周更新，初次爬取全部，后续可根据情况限制页码数量
    陶世玉 2018.12.11
"""


class KuaibaoSpiderSpider(scrapy.Spider):
    name = 'kuaibao_spider'
    # allowed_domains = ['kb.qq.com']
    start_urls = ['http://kb.qq.com/']
    meta = dict()
    custom_settings = {
        'REDIRECT_ENABLED': False,
        "LOG_LEVEL": "DEBUG",
        "ITEM_PIPELINES": {
            'Jovi.pipelines.Redispipline': 200,
            'Jovi.pipelines.Duppipline': 300,
            # # 'Jovi.pipelines.Mongopipline': 400,   #默认不开启MongoDB,节省内存资源
            'Jovi.pipelines.To_csv1': 500
        }
    }
    channels = {
        '互联网': 'kb_news_tech',
        '体育': 'kb_news_sports',
        '娱乐': 'kb_news_bagua',
        '社会': 'kb_news_qipa',
        '时尚': 'kb_news_chaobao',
        '财经': 'kb_news_finance',
        'NBA': 'kb_news_nba'
    }

    def start_requests(self):
        meta = self.meta
        for name, channel in self.channels.items():
            url = 'http://i.match.qq.com/pac/kuaibao?p=1&limit=100&channel={}'.format(channel)
            meta['second_tag'] = name
            meta['channel'] = channel
            meta['page'] = 1
            yield scrapy.Request(url=url, callback=self.get_urls, meta=meta)

    def get_urls(self, response):
        meta = response.meta
        data = json.loads(response.text)
        if data['message'] == '查询成功':
            articles = data['data']
            for article in articles:
                url = article['url']
                meta['title'] = article['title']
                yield scrapy.Request(url=url, callback=self.get_content, meta=meta)
            if meta['page'] < 100:
                meta['page'] += 1
                next_page = 'http://i.match.qq.com/pac/kuaibao?p={}&limit=100&channel={}'.format(meta['page'],
                                                                                                 meta['channel'])
                yield scrapy.Request(url=next_page, callback=self.get_urls, meta=meta)

    def get_content(self, response):
        meta = response.meta
        item = JoviLonglasttimeItem()
        contents = response.xpath('//p[@class="text"]/text() | //h2[@class=""]/text()').extract()
        content = ''
        pattern = r'版权声明|来自:|关注:|搜索：|图：|点击播放|公众号：|文章来源'
        for i in contents:
            if re.search(pattern, i):
                continue
            else:
                content += i.strip()
        # 除了这个版权声明，没有多余的杂质，用replace去除
        # 有需要根据实际情况只设置两层tag,为了简化文档结构，改写相应的pipeline
        item['first_tag'] = '天天快报'
        item['second_tag'] = meta['second_tag']
        item['article_url'] = response.url
        item['article_title'] = meta['title']
        item['article_content'] = content.replace('\n', '').replace('\t', '').replace('\r', '').replace('\u3000',
                                                                                                        '').replace(
            '\xa0', '')
        yield item
