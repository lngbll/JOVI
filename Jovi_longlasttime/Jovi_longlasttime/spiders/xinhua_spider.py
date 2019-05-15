# -*- coding: utf-8 -*-
import json
import re
import time

import scrapy

from Jovi_longlasttime.items import JoviLonglasttimeItem


class XinhuaSpiderSpider(scrapy.Spider):
    name = 'xinhua_spider'
    start_urls = ['http://m.xinhuanet.com/']
    meta = dict()
    log_dir = 'e:\\日志文件夹\\JOVI新闻爬虫\\xinhua_spider'
    date = time.strftime('%Y-%m-%d', time.localtime())
    custom_settings = {
        'LOG_FILE': '{}\\{}.log'.format(log_dir, date),
        'ITEM_PIPELINES': {
            'Jovi_longlasttime.pipelines.Redispipline': 200,
            'Jovi_longlasttime.pipelines.Duppipline': 300,
            'Jovi_longlasttime.pipelines.To_csv1': 500
        }
    }

    def parse(self, response):
        meta = self.meta
        channel_list = response.xpath('//div[@class="nav-list-wrapper"]/ul[@class="channel-list"]/li/a')
        for i in channel_list:
            meta['second_tag'] = i.xpath('text()').extract_first()
            print(meta['second_tag'])
            if meta['second_tag'] not in ['图片', '视频', '广播']:
                href = i.xpath('@href').extract_first()
                if 'http' in href:
                    url = href
                else:
                    url = 'http://m.xinhuanet.com' + href.lstrip('..')
                yield scrapy.Request(url=url, callback=self.get_params, meta=meta)

    # 获取API参数nid,并开始请求第一页
    def get_params(self, response):
        meta = response.meta
        nid = response.xpath('//input[@id="nid"]/@value').extract_first()
        meta['page'] = 1
        meta['nid'] = nid
        json_url = 'http://qc.wa.news.cn/nodeart/list?nid={}&pgnum={}&cnt=12&attr=63&tp=1&orderby=1&mulatt=1'.format(
            nid, meta['page'])
        yield scrapy.Request(url=json_url, callback=self.get_urls, meta=meta)

    # 获取文章url
    def get_urls(self, response):
        meta = response.meta
        json_data = json.loads(response.text.lstrip('(').rstrip(')'))
        try:
            articles = json_data['data']['list']
            for article in articles:
                url = article['LinkUrl']
                meta['article_title'] = article['Title']
                yield scrapy.Request(url=url, meta=meta, callback=self.get_article)
            meta['page'] += 1
            next_page = 'http://qc.wa.news.cn/nodeart/list?nid={}&pgnum={}&cnt=12&attr=63&tp=1&orderby=1&mulatt=1'.format(
                meta['nid'], meta['page'])
            yield scrapy.Request(url=next_page, meta=meta, callback=self.get_urls)
        except KeyError:
            print('%s在第%s页结束或异常' % (meta['second_tag'], meta['page']), end='\n')

    # 爬文章内容
    def get_article(self, response):
        meta = response.meta
        item = JoviLonglasttimeItem()
        contents = response.xpath('//div[@id="p-detail"]/p[not(@class)]/text()').extract()
        content = ''
        pattern = r' 策划：|撰文：'
        for i in contents:
            if re.search(pattern, i):
                continue
            else:
                content += i.strip()
        item['first_tag'] = '新华网'
        item['second_tag'] = meta['second_tag']
        item['article_url'] = response.url
        item['article_title'] = meta['article_title']
        item['article_content'] = content.replace('\r', '').replace('\n', '').replace('\t', '').replace('\xa0',
                                                                                                        '').replace(
            '\u3000', '')
        yield item
