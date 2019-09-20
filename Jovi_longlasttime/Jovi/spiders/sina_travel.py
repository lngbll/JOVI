# -*- coding: utf-8 -*-
import json
import re

import scrapy

from Jovi.items import JoviLonglasttimeItem


class SinaTravelSpider(scrapy.Spider):
    name = 'sina_travel'
    # allowed_domains = ['travel.sina.com.cn']
    start_urls = ['http://travel.sina.com.cn/itinerary/']

    def parse(self, response):
        meta = dict()
        nav = response.xpath('//div[@class="tab-cont__wrap"]/div[position()>1 and position()<9]')
        second_tags = ['国内', '亚洲', '欧洲', '北美洲', '大洋洲', '非洲', '南美洲']
        for i in range(7):
            second_tag = second_tags[i]
            sub_nav = response.xpath('//div[@class="tab-cont__wrap"]/div[%d+2]//span/text()' % i).extract()
            print(sub_nav)
            meta['second_tag'] = second_tag
            for i in sub_nav:
                meta['third_tag'] = i.strip()
                meta['page'] = 1
                url = 'http://interface.sina.cn/travel/inner/list/itinerary_by_dest.d.json?page=1&page_size=10&label={}'.format(
                    meta['third_tag'])
                yield scrapy.Request(url=url, callback=self.get_urls, meta=meta)

    def get_urls(self, response):
        meta = response.meta
        datas = json.loads(response.text)
        data = datas['data']
        if data:
            docs = data['docs']
            for i in docs:
                url = i['url']
                meta['title'] = i['title']
                meta['update_time'] = i['create_time'].split(' ')[0]
                yield scrapy.Request(url=url, callback=self.get_content, meta=meta)
            meta['page'] += 1
            next_page = 'http://interface.sina.cn/travel/inner/list/itinerary_by_dest.d.json?page={}&page_size=10&label={}'.format(
                meta['page'], meta['third_tag'])
            yield scrapy.Request(url=next_page, callback=self.get_urls, meta=meta)

    def get_content(self, response):
        meta = response.meta
        item = JoviLonglasttimeItem()
        contents = response.xpath('//div[@id="artibody"]/p').xpath('string()').extract()
        pattern = r'点击[上下]方|关注(.*?)公众号|关注(.*?)微信|↓|原文|相关阅读|原文|说明：|原标题|原题|选自：|公众号|▲|文章来自|本文|｜|来自网络|作者：|声明：|译自|如有侵权|\||编辑|编者|往期回顾|记者|点击进入|提示：|导语：|转载联系|责编|译者：|来源：'
        content = ''
        for i in contents:
            if re.search(pattern, i):
                continue
            else:
                content += i.strip()
        item['article_content'] = content.replace('\r', '').replace('\t', '').replace('\n', '').replace('\xa0',
                                                                                                        '').replace(
            '\u3000', '').replace('\u200b', '')
        item['article_title'] = meta['title']
        item['article_url'] = response.url
        item['first_tag'] = '新浪游记'
        item['second_tag'] = meta['second_tag']
        item['third_tag'] = meta['third_tag']
        item['update_time'] = meta['update_time']
        item['label'] = ''
        item['source'] = ''
        yield item
