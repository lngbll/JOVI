# -*- coding: utf-8 -*-
import json
import time

import scrapy

from Jovi_longlasttime.items import JoviLonglasttimeItem


class FenghuangAppSpider(scrapy.Spider):
    name = 'fenghuang_app'
    channels = {
        '养生': 'HEALTHLIVE',
        '历史': 'LS153,FOCUSLS153',
        '军事': 'JS83,FOCUSJS83,SECNAVJS83',
        '科技': 'KJ123,FOCUSKJ123,SECNAVKJ123',
        '汽车': 'QC45,FOCUSQC45,SECNAVQC45',
        '时尚': 'SS78,FOCUSSS78,SECNAVSS78',
        'NBA': 'NBAPD,FOCUSNBAPD',
        '萌宠': 'MENGCHONG,FOCUSMENGCHONG',
        '育儿': 'PARENT',
        '政务': 'ZHENGWUPD,FOCUSZHENGWUPD',
        '文化': 'WH25,FOCUSWH25',
        '读书': 'DS57,FOCUSDS57',
        '星座': 'XZ09,FOCUSXZ09',
        '家居': 'JJPD,FOCUSJJPD',
        '教育': 'JY90',
        '美食': 'DELIC,FOCUSDELIC',
        '健康': 'JK36',
        '旅游': 'LY67,FOCUSLY67,SECNAVLY67',
        '国际': 'GJPD,FOCUSGJPD',
    }
    custom_settings = {
        'LOG_LEVEL': 'DEBUG',
        'ITEM_PIPELINES': {},
        'DOWNLOAD_MIDDLEWARES': {},
        'DEPTH_PRIORITY': 1
    }

    def start_requests(self):
        pattern = 'https://api.iclient.ifeng.com/nlist?id={}&action={}&pullNum={}&gv=6.6.5&av=6.6.5&uid=354730010140238' \
                  '&deviceid=354730010140238&proid=ifengnews&os=android_19&df=androidphone&vt=5&' \
                  'screen=720x1280&publishid=2011&nw=wifi&loginid=&st={}&sn=e6012433723c2ba75470963ff182c434'
        meta = dict()
        for category, channel_id in self.channels.items():
            meta['second_tag'] = category
            meta['channel_id'] = channel_id
            url = pattern.format(channel_id, 'default', '', int(1000 * time.time()))
            yield scrapy.Request(url, callback=self.get_article, meta=meta, dont_filter=True)
            for i in range(1, 2):
                url = pattern.format(meta['channel_id'], 'down', i, int(1000 * time.time()))
                yield scrapy.Request(url, callback=self.get_article, meta=meta, dont_filter=True)

    def get_article(self, response):
        print(response.text)
        meta = response.meta
        for block in json.loads(response.text):
            for article in block.get('item'):
                aid = article.get('id')
                # url = 'https://nine.ifeng.com/GetNewsDocs?aid={}&channelId={}&category={}&imId=193374332&' \
                #                 #       'channelKey=&gv=6.6.5&av=6.6.5&uid=354730010140238&deviceid=354730010140238&proid=ifengnews&' \
                #                 #       'os=android_19&df=androidphone&vt=5&screen=720x1280' \
                #                 #       '&publishid=2011&nw=wifi&loginid=&st=15668930951312&sn='.format(aid,meta['channel_id'],meta['second_tag'])
                url = 'https://nine.ifeng.com/GetNewsDocs?aid={}'.format(aid)
                yield scrapy.Request(url, callback=self.get_content, meta=meta, dont_filter=True)

    def get_content(self, response):
        meta = response.meta
        item = JoviLonglasttimeItem()
        data = json.loads(response.text)
        item['first_tag'] = '凤凰新闻'
        item['second_tag'] = meta['second_tag']
        item['article_url'] = response.url
        item['article_title'] = data.get('body').get('title')
        article_content = data.get('body').get('text')
        s = scrapy.Selector(text=article_content)
        item['article_content'] = ''.join(s.xpath('//p//text()').get_all())
        print(item)
        yield item
