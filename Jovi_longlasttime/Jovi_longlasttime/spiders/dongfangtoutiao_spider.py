# -*- coding: utf-8 -*-
import json
import re
import time
import scrapy
from Jovi_longlasttime.items import JoviLonglasttimeItem


class DongfangtoutiaoSpiderSpider(scrapy.Spider):
    name = 'dongfangtoutiao_spider'
    log_dir = 'e:\\日志文件夹\\JOVI新闻爬虫\\dongfangtoutiao_spider'
    date = time.strftime('%Y-%m-%d', time.localtime())
    # allowed_domains = ['mini.eastday.com']
    # start_urls = ['http://mini.eastday.com/']
    headers = {
        'Referer': 'https://mini.eastday.com/'
    }
    cate = {
        '军事': {'军事': 'junshi'},
        '社会': {'社会': 'shehui'},
        '娱乐': {'电视': 'dianshi',
               '电影':'dianying',
               '综艺': 'zongyi',
               '八卦': 'bagua',
               },
        '科技': {'科技': 'keji',
              },
        '体育': {'NBA': 'nba',
                'CBA':'cba',
                '德甲': 'dejia',
               '意甲': 'yijia',
               '中超': 'zhongchao',
               '红彩': 'hongcai',},
        '财经': {'外汇': 'waihui',
               '股票': 'gupiao',
               '基金': 'jijin',
               '期货': 'qihuo',
               '理财': 'licai', },
        '汽车': {'汽车': 'qiche'},
        '健康': { '保健': 'baojian',
                '健身': 'jianshen',
                '心理': 'xinli',
                '饮食': 'yinshi',
                '减肥': 'jianfei',
                },
        '国内': {'国内': 'guonei'},
        '国际': {'国际': 'guoji'},
        '时尚': {'时尚': 'shishang'},
        '历史': {'历史': 'lishi'},
        '游戏': {'游戏': 'youxi'},
        '情感': {'情感': 'qinggan'},
        '家居': {'家居': 'jiaju'},
        '星座': {'星座': 'xingzuo'},
    }
    custom_settings = {
        'LOG_FILE':'{}\\{}.log'.format(log_dir,date),
        'DOWNLOADER_MIDDLEWARES': {
            # 'Jovi_longlasttime.middlewares.ProxyMiddleware':300,
            # 'Jovi_longlasttime.middlewares.UaMiddleware': 400,
            # # 'Jovi_longlasttime.middlewares.SeleniumMiddleware':500,
            # 'Jovi_longlasttime.middlewares.redisMiddleware': 200,
            # 'Jovi_longlasttime.middlewares.RefererMiddleware': 500
            # 初始页需要Referer,才能请求到数据
        },
        'ITEM_PIPELINES':{
            # 'Jovi_longlasttime.pipelines.Redispipline': 200,
        },
        'LOG_LEVEL':'INFO',
        'CONCURRENT_REQUESTS': 500,
        'CONCURRENT_ITEMS': 500
    }
    meta = {
        'first_tag': '东方头条',
        'second_tag': '',
        'third_tag': '',
        'page_num': 1,
        'idx':0,
        'source': '',
        'type': '',
        'title': '',
        'content': ''
    }

    def start_requests(self):
        meta = self.meta
        for i in self.cate.keys():
            meta['second_tag'] = i
            for j in self.cate[i].keys():
                meta['third_tag'] = j
                type = self.cate[i][j]
                meta['type'] = type
                ts = int(time.time() * 1000)
                url = 'https://pcflow.dftoutiao.com/toutiaopc_jrtt/newspool?type={}&uid=15439146142732770&startkey=||||&newkey=|&pgnum=1%idx=0&_={}'.format(type,meta[
                    'page_num'], ts)
                yield scrapy.Request(url=url, callback=self.get_url,headers=self.headers, meta=meta)

    def get_url(self, response):
        meta = response.meta
        meta['page_num'] += 1
        res = json.loads(response.body.decode('utf-8').lstrip('null(').rstrip(')'))
        if 'data' in list(res.keys()) and meta['page_num'] < 1000:
            for i in res['data']:
                url = i['url']
                meta['source'] = i['source']
                meta['title'] = i['topic'].strip()
                yield scrapy.Request(url=url, callback=self.get_content, meta=meta)
            startkey = res['endkey']
            newkey = res['newkey']
            column = len(res['data'])
            meta['idx']+=column
            ts = int(time.time() * 1000)
            next_page = 'https://pcflow.dftoutiao.com/toutiaopc_jrtt/newspool?type={}&uid=15439146142732770&startkey={}&newkey={}&pgnum={}&_={}'.format(meta['type'],startkey,newkey,meta[
                    'page_num'], ts)
            yield scrapy.Request(url=next_page, callback=self.get_url, meta=meta)

    def get_content(self, response):
        meta = response.meta
        next = response.xpath('//a[text()="下一页"]')
        contents = response.xpath('//div[@id="J-contain_detail_cnt"]//text()').extract()
        content = ''
        for i in contents:
            if re.search(r'原标题：|选自：|公众号|▲|文章来自|本文|来源|｜|来自网络|作者：|声明：|译自|如有侵权|\||责任编辑：|编者按|往期回顾|记者|点击进入|联合出品|【精彩推荐】|·',
                         i):
                continue
            else:
                content += i.strip()
        meta['content'] += content
        if next:
            url = 'https://mini.eastday.com/a/' + next.xpath('@href').extract_first()
            yield scrapy.Request(url=url, callback=self.get_content, meta=meta)
        else:
            item = JoviLonglasttimeItem()
            item['first_tag'] = meta['first_tag']
            item['second_tag'] = meta['second_tag']
            item['third_tag'] = meta['third_tag']
            item['source'] = meta['source']
            item['update_time'] = response.xpath('//div[@class="fl"]/i[1]/text()').re_first(r'\d+-\d+-\d+')
            item['article_url'] = re.sub(r'-\d+', '', response.url)
            item['article_title'] = meta['title']
            item['label'] = response.xpath('//ul[@class="tagcns"]/li/a/text()').extract()
            item['article_content'] = meta['content'].replace('\r', '').replace('\n', '').replace('\t', '').replace(
                '\xa0', '').replace('\u3000', '').replace('\ufeff', '')
            yield item
