# -*- coding: utf-8 -*-
import re

import redis
import scrapy
from lxml import etree

from Jovi_longlasttime.items import JoviLonglasttimeItem
import time


class ToutiaoNewSpiderSpider(scrapy.Spider):
    name = 'toutiao_new_spider'
    # allowed_domains = ['']
    log_dir = 'e:\\日志文件夹\\JOVI新闻爬虫\\toutiao_new_spider'
    date = time.strftime('%Y-%m-%d', time.localtime())
    meta = {
        'first_tag': '今日头条',
        'second_tag': '',
        'third_tag': '',
        'en': '',
        'source': '',
        'title': '',
        'label': '',
        'request_num':1
    }
    HTML_entity = {
        "&nbsp;": " ",
        "&lt;": "<",
        "&gt;": ">",
        "&amp;": "&",
        "&quot;": "\"",
        "pos;": "'",
        "&cent;": "￠",
        "&pound;": "£",
        "&yen;": "¥",
        "&euro;": "€",
        "&sect;": "§",
        "&copy;": "©",
        "&reg;": "®",
        "&trade;": "™",
        "&times;": "×",
        "&divide;": "÷",
        "&#x3D;": "="
    }
    cate = {
        'ch/news_tech/':'科技',
        'ch/news_entertainment/':'娱乐',
        'ch/news_car/': '汽车',
        'ch/news_sports/': '体育',
        'ch/news_finance/': '财经',
        'ch/news_military/': '军事',
        'ch/news_world/': '国际',
        'ch/news_fashion/': '时尚',
        'ch/news_travel/': '旅游',
        'ch/news_discovery/': '探索',
        'ch/news_baby/': '育儿',
        'ch/news_regimen/': '养生',
        'ch/news_essay/': '美文',
        'ch/news_game/': '游戏',
        'ch/news_history/':'历史',
        'ch/news_food/':'美食'

    }
    r = redis.Redis(host='localhost', port=6379, db=1)
    custom_settings = {
        'LOG_FILE':'{}\\{}.log'.format(log_dir,date),
        'ITEM_PIPELINES':{
            'Jovi_longlasttime.pipelines.BloomFilterPipeline': 200,
            'Jovi_longlasttime.pipelines.Duppipline': 300,
            # # 'Jovi_longlasttime.pipelines.Mongopipline': 400,   #默认不开启MongoDB,节省内存资源
            'Jovi_longlasttime.pipelines.To_csv1': 500
        }
    }

    def start_requests(self):
        meta = self.meta
        url = 1
        while url:
            url = self.r.spop('toutiao')
            if url != None:
                url = url.decode('utf-8')
                if 'http' in url:
                    yield scrapy.Request(url=url, callback=self.get_content, meta=meta)
                else:
                    url = 'https:' + url
                    yield scrapy.Request(url=url, callback=self.get_content, meta=meta)

    def get_content(self, response):
        meta = response.meta
        res = response.body.decode('utf-8')
        item = JoviLonglasttimeItem()
        try:
            content = re.search(r' content: \'(.*?)\',', res).group(1)
            for k, v in self.HTML_entity.items():
                content = content.replace(k, v)
            article_contents = etree.HTML(content).xpath('//p//text()')
            pattern = r"图片来自|原标题：|选自：|公众号|▲|文章来自|本文|来源|｜|来自网络|作者：|声明：|译自|如有侵权|\||责任编辑：|编者按|往期回顾|记者|点击进入|联合出品|【精彩推荐】|·|责编|源丨|文丨|转载联系"
            article_content = ''
            for i in article_contents:
                text = str(i).strip()
                if re.search(pattern, text, re.S):
                    continue
                else:
                    article_content += i.strip()
            item['article_content'] = article_content.replace('\r', '').replace('\n', '').replace('\t', '').replace(
                '\xa0', '').replace('\u3000', '').replace('\u200b', '')
            item['first_tag'] = meta['first_tag']
            item['article_url'] = response.url
            crumbTag = re.search(r'crumbTag: \'(.*?)\',', res, re.S).group(1)
            item['second_tag'] = self.cate[crumbTag]
            item['article_title'] = re.search(r' title: \'(.*?)\',', res, re.S).group(1).strip()
            yield item
        except:
            if meta['request_num']<15:
                meta['request_num'] += 1
                yield scrapy.Request(url=response.url,callback=self.get_content,meta=meta,dont_filter=True)



