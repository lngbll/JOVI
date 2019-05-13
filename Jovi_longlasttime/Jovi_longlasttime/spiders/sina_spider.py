# -*- coding: utf-8 -*-
import json
import re

import scrapy

from Jovi_longlasttime.items import JoviLonglasttimeItem
import time


class SinaSpiderSpider(scrapy.Spider):
    name = 'sina_spider'
    log_dir = 'e:\\日志文件夹\\JOVI新闻爬虫\\sina_spider'
    date = time.strftime('%Y-%m-%d', time.localtime())
    allowed_domains = ['sina.cn']
    start_urls = ['https://sina.cn/index/nav?vt=4&pos=108&his=0']
    meta = {
        'first_tag': '手机新浪网',
        'second_tag': '',
        'third_tag': '',
        'source': '',
        'update_time': '',
        'title': ''
    }
    custom_settings = {
        'LOG_FILE':'{}\\{}.log'.format(log_dir,date)
    }

    def parse(self, response):
        meta = self.meta
        second_tag_nodes = response.xpath('//nav[contains(@class,"map_nav")]')
        for i in second_tag_nodes:
            meta['second_tag'] = i.xpath('*[1]//text()').extract_first()
            third_tag_nodes = i.xpath('*[position()>1]')
            if meta['second_tag'] not in ['博客', '精品栏目', '视频', '图片', '微博', '地方', '原创', '应用', '游戏', '手游']:
                for j in third_tag_nodes:
                    meta['third_tag'] = j.xpath('span/text()').extract_first()
                    url = j.xpath('@href').extract_first()
                    yield scrapy.Request(url=url, callback=self.get_api, meta=meta)

    def get_api(self, response):
        meta = response.meta
        # res=response.body.decode('utf-8')
        res = response.text
        api = re.search('load_api: \'(.*?)\',', res)
        cid = re.search('data-cid="(.*?)"', res)
        if api and cid:
            api = api.group(1)
            cid = cid.group(1)
            if api != '' and cid != '':
                if 'showcid' in api:
                    cid = cid.replace(',', '%2C')
                    yield scrapy.Request(url='https:' + api + '&col=' + cid + '&page=1', callback=self.get_url,
                                         meta=meta)
                else:
                    url = 'https:' + api + '?col=' + cid + '&page=1'
                    yield scrapy.Request(url=url, callback=self.get_url, meta=meta, encoding='utf-8')

    def get_url(self, response):
        meta = response.meta
        if response.body != b'':
            data = json.loads(response.body.decode('utf-8'))
            pages = data['result']['data']['list']
            for i in pages:
                url = i['URL']
                meta['source'] = i['source']
                if 'showcid' in response.url:
                    meta['update_time'] = i['cdateTime'].split(' ')[0]
                else:
                    meta['update_time'] = i['ctimedate'].split(' ')[0]
                meta['title'] = i['title'].strip()
                yield scrapy.Request(url=url, callback=self.get_content, meta=meta)
            page = re.search(r'page=(\d+)', response.url).group(1)
            next_page = str(int(page) + 1)
            next_url = re.sub(r'page=\d+', 'page=' + next_page, response.url)
            yield scrapy.Request(url=next_url, callback=self.get_url, meta=meta)

    def get_content(self, response):
        meta = response.meta
        if response.body != b'':
            contents = response.xpath('//article/p//text()|//section[@class="art_pic_card art_content"]/p//text()|//div[@class="article"]/p//text()').extract()
            content = ''
            for i in contents:
                if re.search('原标题：|图片来自|图片来源|文章转自|文章来自|本文来源|本文来自|作者：|微信公众号|更多信息请关注|来源：|如有侵权|点击进入专题|作者署名|本文是|ID：|✎|文\|',
                             i):
                    continue
                else:
                    content += i.strip()
            item = JoviLonglasttimeItem()
            item['first_tag'] = meta['first_tag']
            item['second_tag'] = meta['second_tag']
            item['third_tag'] = meta['third_tag']
            item['article_url'] = response.url
            item['source'] = meta['source']
            item['update_time'] = meta['update_time']
            item['article_title'] = meta['title']
            item['article_content'] = content.replace('\r', '').replace('\n', '').replace('\t', '').replace('\xa0',
                                                                                                            '').replace(
                '\u3000', '')
            yield item
