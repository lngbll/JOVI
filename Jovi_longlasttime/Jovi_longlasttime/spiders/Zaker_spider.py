# -*- coding: utf-8 -*-
import json
import re

import scrapy

from Jovi_longlasttime.items import JoviLonglasttimeItem
import time


class ZakerSpiderSpider(scrapy.Spider):
    log_dir = 'e:\\日志文件夹\\JOVI新闻爬虫\\Zaker_spider'
    date = time.strftime('%Y-%m-%d', time.localtime())
    name = 'Zaker_spider'
    allowed_domains = ['www.myzaker.com']
    start_urls = ['http://www.myzaker.com/']

    meta = {
        'first_tag': 'Zaker新闻',
        'second_tag': '',
        'third_tag': '',
        'title': '',
        'page_num': 1

    }
    custom_settings = {
        'LOG_FILE':'{}\\{}.log'.format(log_dir,date),
        'ITEM_PIPELINES': {
            'Jovi_longlasttime.pipelines.Redispipline': 200,
            'Jovi_longlasttime.pipelines.Duppipline': 300,
            # # # 'Jovi_longlasttime.pipelines.Mongopipline': 400,   #默认不开启MongoDB,节省内存资源
            'Jovi_longlasttime.pipelines.To_csv1': 500
        },
        'DOWNLOADER_DELAY':0.5
    }


    def parse(self,response):
        meta = self.meta
        second_tag_node = response.xpath('//div[@class="nav"]/a | //div[@class="nav_menu"]/a')
        for i in second_tag_node:
            meta['second_tag'] = i.xpath('text()').extract_first().strip()
            url = i.xpath('@href').extract_first()
            yield scrapy.Request(url='http:'+url,meta=meta,callback=self.get_first_page)


    def get_first_page(self,response):
        meta = response.meta
        article_urls = response.xpath('//div[@id="section"]//a/@href').extract_first()
        for i in article_urls:
            yield scrapy.Request('http:'+i,meta=meta,callback=self.get_content)
        first_page = response.xpath('//input[@id="nexturl"]/@value').extract_first()
        url = 'http:'+first_page
        yield scrapy.Request(url,meta=meta,callback=self.get_url)

    def get_url(self, response):
        meta = response.meta
        data = json.loads(response.text)
        try:
            for i in data['data']['article']:
                url = i['href']
                yield scrapy.Request(url='http:' + url, callback=self.get_content, meta=meta)
            if 'next_url' in data['data'].keys():
                meta['page_num'] += 1
                yield scrapy.Request(url='http:' + data['data']['next_url'], callback=self.get_url, meta=meta)
        except KeyError:
            print('网页格式有变化，注意更改脚本')


    def get_content(self, response):
        meta = response.meta
        item = JoviLonglasttimeItem()
        item['article_url'] = response.url
        item['first_tag'] = meta['first_tag']
        item['second_tag'] = meta['second_tag']
        host = response.url.split('/')[2]
        print(response.url)
        try:
            if host=='mp.weixin.qq.com':
                item['article_title'] = response.xpath('//*[@id="activity-name"]//text()').extract_first().strip()
                ps = response.xpath('//div[@id="js-content"]/p//text()').extract()

            elif host=='xw.qq.com':
                item['article_title'] = response.xpath('//div[@class="tpl_header_title"]/text()').extract_first().strip()
                ps = response.xpath('//*[@id="cont"]/p//text()').extract()

            elif host == 'www.myzaker.com' or host=='app.myzaker.com':
                item['article_title'] = response.xpath('//h1/text()').extract_first().strip()
                ps = response.xpath('//div[@class="article"]//text() | //div[@id="content" and not(@zk-guide)]/p//text()').extract()

            else:
                return

        except Exception:
            print('something wrong!!')
            return

        content = ''
        for p in ps:
            if re.search(
                    r'责任编辑：|作者：|出处：|{}|来自：|来源 :|来源：|来源 : |图片来自|图片由|图：|更多精彩|请投稿至：|文|文／|编辑'.format(item[ 'article_title']),p):
                continue
            elif re.search(r'关注微信公众号|参考资料|声明：|原网页已经由 ZAKER 转码排版 ', p):
                break
            else:
                content += p.strip()
        item['article_content'] = content.replace('\n', '').replace('\r', '').replace('\t', '').replace('\u3000','').replace('\xa0', '')
        yield item
