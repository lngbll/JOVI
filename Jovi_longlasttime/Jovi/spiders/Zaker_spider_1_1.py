# -*- coding: utf-8 -*-
import json
import re
import time
from urllib.parse import urljoin

import scrapy
from scrapy.log import logger

from Jovi.items import JoviLonglasttimeItem
import os

class ZakerSpider11Spider(scrapy.Spider):
    name = 'Zaker_spider_1_1'
    allowed_domains = ['www.myzaker.com']
    domain = 'http://www.myzaker.com'
    start_urls = ['http://www.myzaker.com/']
    logger = logger
    date = time.strftime('%Y-%m-%d', time.localtime())
    log_dir = os.path.join(os.path.split(__file__)[0], '..', '..', 'log', 'Zaker')
    custom_settings = {
        'LOG_FILE': os.path.join(log_dir,'{}.log'.format(date)),
        'ITEM_PIPELINES': {
            'Jovi.pipelines.BloomFilterPipeline': 200,
            'Jovi.pipelines.Duppipline': 100,
            'Jovi.pipelines.To_csv1': 500
        },
        'LOG_LEVEL': 'ERROR',
        'DOWNLOAD_DELAY': 0.2
    }

    def parse(self, response):
        meta = dict()
        channels = response.xpath('//div[@class="nav-btn all more"]//a')
        self.logger.debug(channels)
        for channel in channels:
            meta['second_tag'] = channel.xpath('text()').get()
            channel_url = urljoin(self.domain, channel.xpath('@href').get())
            yield scrapy.Request(channel_url, meta=meta, callback=self.get_first_xhr)

    def get_first_xhr(self, response):
        meta = response.meta
        article_urls = re.search(r'"recommend_arr":(.*?),"article_new_arr"', response.text, re.S).group(1)
        article_urls = json.loads(article_urls)
        article_urls = article_urls.get('value')
        for i in article_urls:
            meta['article_title'] = i.get('title')
            article_url = urljoin(self.domain, i.get('url'))
            meta['article_url'] = article_url
            yield scrapy.Request(article_url, meta=meta, callback=self.parse_article)
        first_xhr = re.search(r'"seo_next_url":(.*?),"next_url_html"', response.text, re.S)
        if first_xhr:
            first_xhr = first_xhr.group(1)
            first_xhr = json.loads(first_xhr).get('value')
            first_xhr = urljoin(self.domain, first_xhr)
            yield scrapy.Request(first_xhr, meta=meta, callback=self.for_xhr)
        else:
            self.logger.debug('没有下一页\t%s' % response.url)

    def for_xhr(self, response):
        meta = response.meta
        res = json.loads(response.text)
        articles = res.get('data').get('article')
        for article in articles:
            meta['article_title'] = article.get('title')
            article_url = urljoin(self.domain, (article.get('url') if article.get('url') else article.get('href')))
            meta['article_url'] = article_url
            yield scrapy.Request(article_url, meta=meta, callback=self.parse_article)
        # 用seo_next_url比较好
        seo_next_url = res.get('seo_next_url')
        if seo_next_url:
            next_xhr = seo_next_url.get('value')
        else:
            next_xhr = res.get('data').get('next_url')
        # 如果结果不为空，请求下一页
        if next_xhr:
            next_xhr = urljoin(self.domain, next_xhr)
            yield scrapy.Request(next_xhr, meta=meta, callback=self.for_xhr)
        else:
            self.logger.debug('没有下一页%s' % response.url)

    def parse_article(self, response):
        meta = response.meta
        item = JoviLonglasttimeItem()
        ps = response.xpath('//div[@id="content"]/p/text()').getall()
        content = ''.join(map((lambda x: x.strip().replace('\n', '').replace('\r', '')), ps))
        item['article_url'] = meta['article_url']
        item['first_tag'] = 'Zaker新闻'
        item['second_tag'] = meta['second_tag']
        item['article_title'] = meta['article_title']
        item['article_content'] = content
        yield item
