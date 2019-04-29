# -*- coding: utf-8 -*-
import codecs
import json
import re
import time

import scrapy
from lxml import etree

from Jovi_longlasttime.items import BlogItem


class WeibonameSpider(scrapy.Spider):
    name = 'weiboname'
    # allowed_domains = ['d.weibo.com']

    headers1 = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # 'Cookie':'SINAGLOBAL=3265554702852.2134.1540779784224; login_sid_t=0697083a3b69b58897a4414937f3d4f4; cross_origin_proto=SSL; _s_tentry=www.google.com.hk; Apache=5008793828465.738.1540948385179; ULV=1540948385184:5:5:5:5008793828465.738.1540948385179:1540894202202; YF-Page-G0=140ad66ad7317901fc818d7fd7743564; wb_view_log_5234071528=1920*10801; TC-Page-G0=8dc78264df14e433a87ecb460ff08bfe; crossidccode=CODE-gz-1GhG3L-27QukX-tO6pSQMtAv9ItC1528bc5; appkey=; UOR=www.google.com.hk,www.weibo.com,login.sina.com.cn; SUHB=0rrLlFGBxYCsch; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WhTFGMYuXqMc8ZBnmZuAPaL5JpV2K27SoeNSK5RSKi5MP2Vqcv_; SUB=_2AkMshZ1bdcPxrAZTm_wVy2rnboVH-jyfUPStAn7uJhMyAxgv7ksuqSVutBF-XE_eQDhy4xpNxXGbFAZWo_puubSw',
        'Pragma': 'no-cache',
        'Host': 'd.weibo.com',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://d.weibo.com/1087030002_417',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'
    }
    headers2 = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'UOR=www.google.com.hk,www.weibo.com,www.google.com.hk; SINAGLOBAL=3265554702852.2134.1540779784224; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhTFGMYuXqMc8ZBnmZuAPaL5JpX5o275NHD95QfeoeXehMpSKzRWs4Dqcj_i--ci-zfiK.Xi--4iK.Ri-z0i--fiKysi-2Xi--4iKn0i-2pi--Xi-iWi-iW; wvr=6; login_sid_t=09d9ff5cbf90a191b23d6d0f8fa397d8; cross_origin_proto=SSL; _s_tentry=login.sina.com.cn; Apache=350936852158.70306.1540862436357; ULV=1540862436361:3:3:3:350936852158.70306.1540862436357:1540794341510; ALF=1572398777; SSOLoginState=1540862778; SUB=_2A25208NuDeRhGeNM6FYR9y_JyTSIHXVVqLOmrDV8PUNbmtBeLWv5kW9NTj-aGnKufPveOw_apIj9mlR8ncwURc26; SUHB=0wnF-vWnU1QL4-; TC-Page-G0=c9fb286cd873ae77f97ce98d19abfb61; wb_view_log_5234071528=1920*10801; YF-Page-G0=416186e6974c7d5349e42861f3303251',
        'Host': 'd.weibo.com',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',

    }
    headers3 = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'UOR=www.google.com.hk,www.weibo.com,www.google.com.hk; SINAGLOBAL=3265554702852.2134.1540779784224; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhTFGMYuXqMc8ZBnmZuAPaL5JpX5o275NHD95QfeoeXehMpSKzRWs4Dqcj_i--ci-zfiK.Xi--4iK.Ri-z0i--fiKysi-2Xi--4iKn0i-2pi--Xi-iWi-iW; wvr=6; login_sid_t=09d9ff5cbf90a191b23d6d0f8fa397d8; cross_origin_proto=SSL; _s_tentry=login.sina.com.cn; Apache=350936852158.70306.1540862436357; ULV=1540862436361:3:3:3:350936852158.70306.1540862436357:1540794341510; ALF=1572398777; SSOLoginState=1540862778; SUB=_2A25208NuDeRhGeNM6FYR9y_JyTSIHXVVqLOmrDV8PUNbmtBeLWv5kW9NTj-aGnKufPveOw_apIj9mlR8ncwURc26; SUHB=0wnF-vWnU1QL4-; TC-Page-G0=c9fb286cd873ae77f97ce98d19abfb61; wb_view_log_5234071528=1920*10801; YF-Page-G0=416186e6974c7d5349e42861f3303251',
        'Host': 'd.weibo.com',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',

    }
    custom_settings = {
        'DOWNLOAD_DELAY': '0.5',

    }

    def start_requests(self):
        url = 'https://d.weibo.com/1087030002_417'
        yield scrapy.Request(url=url, callback=self.parse, headers=self.headers1)

    def parse(self, response):
        meta = dict()
        print(response.text)
        data = re.findall(r'<script>parent\.FM\.view\((.*?)\)</script>', response.text)[5]
        data = json.loads(data)
        html = codecs.escape_decode(bytes(data['html'], encoding='utf-8'))[0].decode('utf-8')
        names = etree.HTML(html).xpath('//ul[@class="ul_item clearfix"]/li/a/span[2]/text()')
        hrefs = etree.HTML(html).xpath('//ul[@class="ul_item clearfix"]/li/a/@href')
        for k, v in dict(zip(names, hrefs)):
            meta['first_tag'] = str(k).strip()
            url = v
            if 'https' in k:
                url = url
            else:
                url = 'https:' + url
            yield scrapy.Request(url, callback=self.get_nav, meta=meta, headers=self.headers2)

    def get_nav(self, response):
        meta = response.meta
        data = re.findall(r'<script>FM\.view\((.*?)\)</script>', response.text)[17]
        data = json.loads(data)
        html = codecs.escape_decode(bytes(data['html'], encoding='utf-8'))[0].decode('utf-8')
        names = etree.HTML(html).xpath('//li[@class="li_text"]/a/text()')
        hrefs = etree.HTML(html).xpath('//li[@class="li_text"]/a/@href')
        for k, v in dict(zip(names, hrefs)):
            meta['second_tag'] = str(k).strip()
            url = v
            if 'https' in k:
                url = url
            else:
                url = 'https:' + url
            yield scrapy.Request(url, callback=self.get_pages, meta=meta, headers=self.headers3)

    def get_pages(self, response):
        meta = response.meta
        data = re.findall(r'<script>FM\.view\((.*?)\)</script>', response.text)[18]
        data = json.loads(data)
        html = codecs.escape_decode(bytes(data['html'], encoding='utf-8'))[0].decode('utf-8')
        page_num = etree.HTML(html).xpath('//div[@class="W_pages"]/a[last()-1]/text()')
        page_num = int(str(page_num))
        _t = 'FM_' + str(int(time.time() * 10000))
        for i in range(1, page_num + 1):
            url = response.url + '?pids=Pl_Core_F4RightUserList__4&page={}&ajaxpagelet=1&_t={}'.format(i, _t)
            yield scrapy.Request(url, callback=self.get_content, meta=meta, headers=self.headers3, dont_filter=True)

    def get_content(self, response):
        meta = response.meta
        data = re.findall(r'<script>FM\.view\((.*?)\)</script>', response.text)[0]
        data = json.loads(data)
        html = codecs.escape_decode(bytes(data['html'], encoding='utf-8'))[0].decode('utf-8')
        item = BlogItem()
        lists = etree.HTML(html).xpath('//ul[@class="follow_list"]/li')
        for list in lists:
            item['first_tag'] = meta['first_tag']
            item['second_tag'] = meta['second_tag']
            item['name'] = list.xpath('//a[@class="S_txt1"]/@title')
            item['guanzhu'] = list.xpath('//div[@class="info_connect"]/span[1]/em[@class="count"]/text()')
            item['fans'] = list.xpath('//div[@class="info_connect"]/span[2]/em[@class="count"]/text()')
            item['articles'] = list.xpath('//div[@class="info_connect"]/span[3]/em[@class="count"]/text()')
            item['address'] = list.xpath('//div[@class="info_add"]/span/text()')
            item['intro'] = list.xpath('//div[@class="info_intro"]/span/text()')
            yield item
