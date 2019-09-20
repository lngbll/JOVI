# -*- coding: utf-8 -*-
import json
import os
import time
from urllib import parse

import scrapy

from Jovi.items import create_item_class


class AutohomeSpider(scrapy.Spider):
    name = 'autoHome_spider'
    allowed_domains = ['www.autohome.com.cn']
    start_urls = ['http://www.autohome.com.cn/all']
    base_url = 'http://www.autohome.com.cn/'
    itemList = ['first_tag', 'second_tag', 'third_tag', 'article_url', 'article_title', 'article_content']
    items = create_item_class('AutoHomeItem', itemList)
    log_dir = os.path.join(os.path.split(__file__)[0], '..', '..', 'log', '汽车之家')
    date = time.strftime('%Y-%m-%d', time.localtime())
    custom_settings = {
        'LOG_FILE': os.path.join(log_dir, '{}.log'.format(date)),
        'DEPTH_PRIORITY': 0
    }

    def parse(self, response):
        meta = dict()
        channels = response.xpath('//*[@id="ulNav"]/ul/li/a')
        for i in channels:
            secondTag = i.xpath('text()').get().strip()
            _url = i.xpath('@href').get()
            url = parse.urljoin(self.base_url, _url)
            meta['second_tag'] = secondTag
            yield scrapy.Request(url=url, meta=meta, callback=self.get_second_tag)

    def get_second_tag(self, response):
        meta = response.meta
        flag = response.xpath('//*[@id="div-fouc-tx"]')
        if flag:
            thirdTags = flag.xpath('ul/li/a')
            for i in thirdTags:
                third_tag = i.xpath('text()').get().strip()
                meta['third_tag'] = third_tag
                classID = i.xpath('@data-class').get()
                meta['classId'] = classID
                url = 'https://www.autohome.com.cn/ashx/channel/AjaxChannelArtList.ashx?20&page=1&class2Id={}'.format(
                    classID)
                yield scrapy.Request(url=url, meta=meta, callback=self.get_pages)

    def get_pages(self, response):
        meta = response.meta
        jt = json.loads(response.text)
        total = jt[0].get('Total')
        pages = (total - 60) // 15 + 1
        for i in range(1, pages + 1):
            page = 'https://www.autohome.com.cn/ashx/channel/AjaxChannelArtList.ashx?20&page={}&class2Id={}'.format(i,
                                                                                                                    meta[
                                                                                                                        'classId'])
            yield scrapy.Request(url=page, meta=meta, callback=self.parse_json, dont_filter=True)

    def parse_json(self, response):
        meta = response.meta
        jt = json.loads(response.text)
        articles = jt[0].get('Article')
        for article in articles:
            meta['article_title'] = article['Title']
            url = 'https://www.autohome.com.cn{}{}/{}.html'.format(article['Dir'], article['PublishTime'],
                                                                   article['Id'])
            yield scrapy.Request(url=url, meta=meta, callback=self.separate)

    def separate(self, response):
        meta = response.meta
        isEnd = response.xpath('//a[text()="阅读全文"]')
        if isEnd:
            url = parse.urljoin(self.base_url, isEnd.xpath('@href').get())
            yield scrapy.Request(url=url, meta=meta, callback=self.get_content)
        else:
            yield scrapy.Request(url=response.url, meta=meta, callback=self.get_content, dont_filter=True)

    def get_content(self, response):
        meta = response.meta
        ps = response.xpath('//*[@id="articleContent"]/p//text() | //*[@class="allread-title"]//text()').getall()
        article_content = ''.join(map((lambda x: x.strip()), ps))
        item = self.items()
        item['first_tag'] = '汽车之家'
        item['second_tag'] = meta['second_tag']
        item['third_tag'] = meta['third_tag']
        item['article_url'] = response.url
        item['article_title'] = meta['article_title']
        item['article_content'] = article_content
        yield item
