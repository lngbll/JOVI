# -*- coding: utf-8 -*-
import json
import re
import time

import scrapy

from Jovi_longlasttime.items import JoviLonglasttimeItem


class FenghuangNewSpiderSpider(scrapy.Spider):
    name = 'fenghuang_new_spider'

    log_dir = 'e:\\日志文件夹\\JOVI新闻爬虫\\fenghuang_new_spider'
    date = time.strftime('%Y-%m-%d', time.localtime())


    # allowed_domains = ['i.ifeng.com']
    start_urls = ['http://i.ifeng.com/']
    meta = {
        'first_tag': '手机凤凰网',
        'second_tag': '',
        'third_tag': '',
        'page': 1
    }
    api = {
        '新闻': 'https://inews.ifeng.com/32_0/data.shtml?_={}',
        '娱乐': 'http://ient.ifeng.com/14_{}/data.shtml?_={}',
        '财经': 'http://ifinance.ifeng.com/1_{}/data.shtml?_={}',
        '军事': 'https://imil.ifeng.com/20_{}/data.shtml?_={}',
        '科技': 'http://itech.ifeng.com/7_{}/data.shtml?_={}',
        '体育': 'https://isports.ifeng.com/tjwData/{}/data.shtml?_={}',
        '时尚': 'http://ifashion.ifeng.com/10004_{}/data.shtml?_={}',
        '历史': 'https://ihistory.ifeng.com/21_{}/data.shtml?_={}',
        '公益': 'https://igongyi.ifeng.com/10008_{}/data.shtml?_={}',
        '文化': 'https://iculture.ifeng.com/10009_{}/data.shtml?_={}',
        '国学': 'https://iguoxue.ifeng.com/10008_{}/data.shtml?_={}',
        '社会': 'https://i.ifeng.com/idyn/inews/0/7720/{}/10/data.shtml',
    }

    custom_settings = {
        'LOG_FILE': '{}\\{}.log'.format(log_dir, date),
        'ITEM_PIPELINES':{
            'Jovi_longlasttime.pipelines.Redispipline': 200,
            'Jovi_longlasttime.pipelines.Duppipline': 300,
            # # 'Jovi_longlasttime.pipelines.Mongopipline': 400,   #默认不开启MongoDB,节省内存资源
            'Jovi_longlasttime.pipelines.To_csv1': 500
        }
    }
    def start_requests(self):
        meta = self.meta
        for k, v in self.api.items():
            meta['second_tag'] = k
            # url = v.formaat(int(time.time()*1000))
            meta['page'] = 1
            if meta['second_tag'] == '社会':
                url = v.format(meta['page'] - 1)
            else:
                url = v.format(meta['page'] - 1, int(time.time() * 1000))
            print('开始爬%s的第%s页' % (meta['second_tag'], meta['page']))
            yield scrapy.Request(url, callback=self.get_url, meta=meta)

    def get_url(self, response):
        meta = response.meta
        html = response.text.lstrip('getListDatacallback(').rstrip(');')
        data = json.loads(html)
        for i in data:
            if meta['second_tag'] == '体育':
                id = i['wemediaEArticleId']
                url = 'https://ifenghuanghao.ifeng.com/{}/news.shtml'.format(id)
            else:
                id = i['pageUrl']
                if meta['second_tag'] == '社会':
                    url = id
                else:
                    url = '/'.join(response.url.split('/')[0:3]) + id
            print(url)
            meta['title'] = i['title']
            yield scrapy.Request(url=url, callback=self.get_content, meta=meta)
        if response.text != 'getListDatacallback([]);':
            if meta['second_tag'] == '社会':
                nextPage = 'https://i.ifeng.com/idyn/inews/0/7720/{}/10/data.shtml'.format(meta['page'] * 10)
            elif meta['second_tag'] == '体育':
                nextPage = response.url.replace(response.url.split('/')[-2], str(meta['page'])).replace(
                    response.url.split('=')[-1], str(int(time.time() * 1000)))
            else:
                nextPage = re.sub(r'_\d+/', '_' + str(meta['page']) + '/', response.url).replace(
                    response.url.split('=')[-1], str(int(time.time() * 1000)))
            meta['page'] += 1
            print('开始爬%s的第%s页' % (meta['second_tag'], meta['page']))
            yield scrapy.Request(nextPage, callback=self.get_url, meta=meta, dont_filter=True)

    def get_content(self, response):
        meta = response.meta
        item = JoviLonglasttimeItem()

        contents = response.xpath('//div[@id="whole_content"]/p/text()').extract()
        # header = response.xpath('//div[contain(@class,"acTxtTit ")]//span')
        content = ''
        pattern = r'/|图\d：|图文|说明：|原标题|原题|选自：|公众号|▲|文章来自|本文|来源|｜|来自网络|作者：|声明：|译自|如有侵权|\||编辑|编者|往期回顾|记者|点击进入|联合出品|图为|提示：|导语：|资料图|图注：'
        for i in contents:
            if re.search(pattern, i, re.S):
                continue
            else:
                content += i.strip()
        item['article_content'] = content.replace('\r', '').replace('\n', '').replace('\t', '').replace('\u3000',
                                                                                                        '').replace(
            '\xa0', '').replace('\u200b', '')
        item['first_tag'] = '手机凤凰网'
        item['second_tag'] = meta['second_tag']
        item['update_time'] = response.xpath('//div[contains(@class,"acTxtTit ")]//span[1]/text()').extract_first()
        item['source'] = response.xpath('//div[contains(@class,"acTxtTit ")]//span[last()]/text()').extract_first()
        item['article_title'] = meta['title']
        item['article_url'] = response.url
        yield item
