# -*- coding: utf-8 -*-
import json
import re

import scrapy

from Jovi_longlasttime.items import JoviLonglasttimeItem
import time


class TencentNewSpiderSpider(scrapy.Spider):
    name = 'tencent_new_spider'
    log_dir = 'e:\\日志文件夹\\JOVI新闻爬虫\\tengxun_spider'
    date = time.strftime('%Y-%m-%d', time.localtime())
    # allowed_domains = ['www.qq.com']
    custom_settings = {'LOG_FILE':'{}\\{}.log'.format(log_dir,date)}
    start_urls = ['http://www.qq.com/']
    ext = {
        '军事': 'milite',
        '娱乐': {
            '电影': '101',
            '电视剧': '102,111,113',
            '综艺': '103',
            '音乐': '105',
            '明星': '106,118,108',
        },
        '体育': {
            'NBA': '203,210,229',
            'CBA': '209',
            '中超': '222,225,223',
            '意甲': '220',
            '英超': '221',
            '田径': '201',
        },
        '国际': '',
        '科技': {
            '互联网': '614,603,605,611,612,613,615,620,618',
            '通信_传统IT': '604,609',
            '人工智能': '602,608,622',
            '创业创新': '619,617,610',
            '前沿科技': '607,616,623,624',
        },
        '财经': {
            '宏观经济': '3909,3916',
            '产业公司': '3913,3914,3915,',
            '金融市场': '3906,3902,3907,3908',
            '银行': '3901,3902,3903,3917',
            '基金': '3904,3908,3910',
            '保险': '3906,3901,3910',
        },
        '汽车': 'auto',
        '时尚': {
            '奢侈珠宝': '55,7,5502,5505,5506,5530',
            '潮流时装': '7,5503,5532,5533,8101,8102',
            '化妆护肤': '7,5507,550,5509,551,5529,550,5520,552,5522,5523',
            '瘦身塑形': '7603,7606,7608,7609,7613,215,216,5501',
        },
        '游戏': 'games',
        '房产': {
            '租赁中介': '4006',
            '楼盘销售': '4009',
            '装修': '7401',
            '家电': '7404',
            '家具': '7406',
            '植物': '7405',
        },
        '文化': {
            '文学': '911,914',
            '艺术': '903,904,905,907,910',
            '收藏': '902,906,908,915',
            '思想': '912,916',
            '民俗': '913',
        },
        '动漫': 'comic',
        '情感': 'emotion',
        '星座': 'astro',
        '健康': {
            '减肥健身': '1401,7603,7603,1401,7605,7606,7608,7609,7613,7610,7605',
            '养生': '1402,1421',
            '中医': '1403,1421',
            '疾病防治': '1411',
            '老人健康': '1412',
            '育儿健康': '1417,43',
            '饮食健康': '1419,1420',
        },
        '生活': 'life',
        '旅游': {
            '非洲美洲': '1201,1202,1215',
            '国内旅游': '1203,1206,1210,1211,1214',
            '港澳台游': '1205',
            '日韩旅游': '1207,1212',
            '东南亚游': '1208,1216,1217',
            '澳洲旅游': '1209',
            '自驾游': '1210',
            '旅游路线': '1211',
            '周边游': '1214',

        },
        '美食': 'food',
        '母婴': {
            '孕产': '4301,4304,4305',
            '喂养': '4303,4305',
            '亲子': '4302',
            '萌娃': '4306',
        },
        '宠物': 'pet',
        '时政': 'msh',
        '足球': 'sports_football',
        '教育': {
            '高校': '3502,',
            '考研': '3506,3513',
        },
        '证券': 'finance_stock',
    }
    meta = {
        'first_tag': '腾讯新闻',
        'secong_tag': '',
        'third_tag': '',
        'update_time': '',
        'source': '',
    }

    def start_requests(self):
        meta = self.meta
        for i in self.ext.keys():
            if type(self.ext[i]) == str:
                meta['second_tag'] = i
                meta['third_tag'] = i
                url = 'https://pacaio.match.qq.com/irs/rcd?cid=58&token=c232b098ee7611faeffc46409e836360&ext={}&page=0'.format(
                    self.ext[i])
                yield scrapy.Request(url, callback=self.get_url, meta=meta)
            else:
                for j in self.ext[i].keys():
                    meta['second_tag'] = i
                    meta['third_tag'] = j
                    url = 'https://pacaio.match.qq.com/irs/rcd?cid=52&token=8f6b50e1667f130c10f981309e1d8200&ext={}&page=0'.format(
                        self.ext[i][j])
                    yield scrapy.Request(url, callback=self.get_url, meta=meta)

    def get_url(self, response):
        meta = response.meta
        text = response.body.decode('utf-8')
        resp = json.loads(text)
        data = resp['data']
        if data != []:
            for i in data:
                url = i['vurl']
                meta['update_time'] = re.search(r'\d+-\d+-\d+', i['update_time']).group()
                meta['source'] = i['source']
                # 发现如果不用https会重定向
                if url.split(':')[0] == 'https':
                    url = url
                else:
                    url = url.replace('http', 'https')
                # 这个url还有个坑
                if 'html' in url:
                    url = url
                else:
                    url = url.rstrip('00') + '.html'
                yield scrapy.Request(url=url, callback=self.get_content, meta=meta)
            page = int(re.search(r'page=(\d+)', response.url).group(1))
            next_page = response.url.replace('page=' + str(page), 'page=' + str(page + 1))
            yield scrapy.Request(url=next_page, callback=self.get_url, meta=meta)

    def get_content(self, response):
        if response.body:
            meta = response.meta
            item = JoviLonglasttimeItem()
            url = response.url
            item['article_title'] = response.xpath('//h1/text()').extract_first()
            contents = response.xpath('//*[@class="content-article"]/p').xpath('string()').extract()
            content = ''
            for i in contents:
                if re.search(r'原标题：|图片来自|图片来源|作者：|微信公众号|更多信息请关注|来源：', i):
                    continue
                else:
                    content += i.strip()
            item['article_content'] = content.replace('\r', '').replace('\n', '').replace('\t', '').replace('\u3000',
                                                                                                            '').replace(
                '\xa0', '')
            item['article_url'] = url
            item['first_tag'] = meta['first_tag']
            item['second_tag'] = meta['second_tag']
            item['third_tag'] = meta['third_tag']
            item['update_time'] = meta['update_time']
            item['source'] = meta['source']
            yield item
