# -*- coding: utf-8 -*-
import json
import re

import scrapy

from Jovi_longlasttime.items import JoviLonglasttimeItem


class A163spiderSpider(scrapy.Spider):
    name = '163spider'
    # allowed_domains = ['3g.163.com']
    category = {
        '新闻': {
            '国内': 'BD29LPUBwangning',
            '国际': 'BD29MJTVwangning',
            '历史': 'C275ML7Gwangning',
        },
        '娱乐': {
            '电视': 'BD2A86BEwangning',
            '电影': 'BD2A9LEIwangning',
            '明星': 'BD2AB5L9wangning',
            '音乐': 'BD2AC4LMwangning',
            '影视歌': 'C2769L6Ewangning'
        },
        '体育': {
            'NBA': 'BD2AQH4Qwangning',
            '国际足球': 'BD2ATMK0wangning',
            '中超': 'BD2ASUDCwangning',
            'CBA': 'BD2ARVG2wangning',
            '英超': 'C0PJJIGKbjlvxin',

        },
        '财经': {
            '股票': 'BD2C01CQwangning',
            '基金': 'BD2C1904wangning',
            '商业': 'BD2C24VCwangning',
        },
        '汽车': {
            '汽车观察': 'DE0E57UJwangning'
        },
        '军事': {
            '军情': 'DE0CGUSJwangning',  # 军情多为图集
            '军品': 'DE0CE1U2wangning',  # 军品几乎都是图集
        },
        '科技': {
            '科学': 'D90S2KJMwangning',
            '智能': 'D90S5T8Qwangning',
        },
        '手机': {
            '安卓': 'BV5U5EOVwangning',
            '苹果': 'BV5U6ON6wangning'
        },
        '数码': {
            '数码': 'BAI6JOD9wangning',
        },
        '网易号': {
            '每日推荐': 'BBM50AKDwangning'
        },
        '时尚': {
            '首页': 'BA8F6ICNwangning',  # 首页和情爱明显内容不同
            '情爱': 'BD2BDNBPwangning'
        },
        '游戏': {
            '游戏': 'BAI6RHDKwangning'
        },
        '教育': {
            '留学': 'BD2DGFADwangning',
            '移民': 'BD2DHAH1wangning',
            '外语': 'BD2DIR3Gwangning',
        },
        '健康': {
            '健康': 'BDC4QSV3wangning'
        },
        '旅游': {
            '旅游': 'BEO4GINLwangning'
        },
        '亲子': {
            '亲子': 'BEO4PONRwangning'
        },
        '艺术': {
            '艺术': 'CKKS0BOEwangning'
        },
        '双创': {
            '快讯': 'CQU8M71Llizhenzhen',
            '初创': 'CQU8PU50lizhenzhen',
            '大公司': 'QU8RUS5lizhenzhen',
            '方法论': 'CQU8TUQDlizhenzhen  ',
            '服务': 'CQU8VOR3lizhenzhen',
        },
        '彩票': {
            '彩市新闻': 'BVAU05FVwangning',
            '双色球': 'BVAU19R7wangning',
            '大乐透': 'BVAU268Hwangning',
            '足彩': 'BVAU318Uwangning',
        }

    }
    meta = {
        'first_tag': '手机网易网',
        'second_tag': '',
        'third_tag': '',
        'source': '',
        'update_time': '',
        'title': ''
    }

    custom_settings = {
        # 'DEPTH_PRIORITY':1,
        # 'LOG_LEVEL':'DEBUG',
        # 'DOWNLOADER_MIDDLEWARES':{
        #         #     'Jovi_longlasttime.middlewares.ProxyMiddleware': 300,
        #         #     'Jovi_longlasttime.middlewares.UaMiddleware': 400,
        #         #     'Jovi_longlasttime.middlewares.SeleniumMiddleware': 500,
        #         #     'Jovi_longlasttime.middlewares.redisMiddleware': 200
        #         # },
        'ITEM_PIPELINES' : {
            'Jovi_longlasttime.pipelines.Redispipline': 200,
            'Jovi_longlasttime.pipelines.Duppipline': 300,
            # 'Jovi_longlasttime.pipelines.Mongopipline': 400,
            'Jovi_longlasttime.pipelines.To_csv': 500
        }
    }
    def start_requests(self):
        meta = self.meta
        for i in self.category.keys():
            meta['second_tag'] = i
            for j in self.category[i].keys():
                meta['third_tag'] = j
                for k in range(0, 310, 10):
                    url = 'https://3g.163.com/touch/reconstruct/article/list/{}/{}-10.html'.format(self.category[i][j],
                                                                                                   k)
                    yield scrapy.Request(url=url, callback=self.get_url, meta=meta)

    def get_url(self, response):
        meta = response.meta
        data = json.loads(response.body.decode('utf-8').replace('artiList(', '').replace(')', ''))
        cate = response.url.split('/')[-2]
        for i in data[cate]:
            if 'skipType' not in i.keys():  # 过滤图集和视频
                meta['source'] = i['source']
                meta['update_time'] = i['ptime'].split(' ')[0]
                meta['title'] = i['title'].strip()
                docid = i['docid']
                url = 'https://3g.163.com/dy/article/{}.html'.format(docid)
                yield scrapy.Request(url=url, callback=self.get_content, meta=meta)

    def get_content(self, response):
        meta = response.meta
        contents = response.xpath('//div[contains(@class,"page js-page")]/p//text()').extract()
        content = ''
        for i in contents:
            if re.search(r'原标题：|选自：|公众号|▲|文章来自|本文|来源|｜|来自网络|作者：|声明：|译自|如有侵权|\||编辑：|编者按|往期回顾|记者|点击进入|联合出品|【精彩推荐】|·', i):
                continue
            else:
                content += i.strip()

        item = JoviLonglasttimeItem()
        item['first_tag'] = meta['first_tag']
        item['second_tag'] = meta['second_tag']
        item['third_tag'] = meta['third_tag']
        item['label'] = ''
        item['source'] = meta['source']
        item['update_time'] = meta['update_time']
        item['article_url'] = response.url
        item['article_title'] = meta['title']
        item['article_content'] = content.replace('\r', '').replace('\n', '').replace('\t', '').replace('\xa0',
                                                                                                        '').replace(
            '\u3000', '')
        yield item
