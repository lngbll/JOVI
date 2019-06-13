# -*- coding: utf-8 -*-
'''
    2009.4.29   搜狐视频体育板块之前是爬搜狐滚动体育，突然数据很少，改爬搜狐体育板块，由于小版块很多，格式也不一样，选择了一部分板块
                。进入下级板块，html中有json加载连接。
'''

import json,time
import re
import time
import scrapy
from Jovi_longlasttime.items import JoviLonglasttimeItem


class SohuSpiderSpider(scrapy.Spider):
    name = 'sohu_spider'
    # allowed_domains = ['www.sohu.com']
    log_dir = 'e:\\日志文件夹\\JOVI新闻爬虫\\sohu_spider'
    date = time.strftime('%Y-%m-%d', time.localtime())
    start_urls = ['http://gov.sohu.com/']
    custom_settings = {
        'LOG_FILE':'{}\\{}.log'.format(log_dir,date),
    }
    channels = {
        '新闻':'http://www.sohu.com/c/8',
        '汽车':'http://www.sohu.com/c/18',
        '旅游': 'http://travel.sohu.com',
        '教育': 'http://learning.sohu.com',
        '时尚': 'http://fashion.sohu.com/1045',
        '科技': 'http://it.sohu.com',
        '财经': 'http://business.sohu.com',
        '母婴': 'http://baobao.sohu.com',
        '健康': 'http://baobao.sohu.com',
        '历史': 'http://history.sohu.com',
        '军事': 'http://mil.sohu.com',
        '美食': 'http://chihe.sohu.com',
        '文化': 'http://cul.sohu.com',
        '星座': 'http://astro.sohu.com',
        '游戏': 'https://game.sohu.com',
        '动漫': 'http://acg.sohu.com',
        '宠物': 'http://pets.sohu.com',
        '体育':'http://sports.sohu.com'
    }
    def start_requests(self):
        meta = dict()
        meta['first_tag'] = '搜狐网'
        for i in self.channels.keys():
            meta['second_tag'] = i
            url = self.channels[i]
            if i=='体育':
                yield scrapy.Request(url=url, meta=meta, callback=self.parse_sports)
            else:
                yield scrapy.Request(url=url, meta=meta, callback=self.parse_second_nav)


    def parse_sports(self,response):
        meta = response.meta
        second_tag_nodes = response.xpath('//div[@class="sports-navs"]//a[@class="link-txt"]')
        for i in second_tag_nodes:
            meta['third_tag'] = i.xpath('text()').extract_first().strip()
            if meta['third_tag'] not in ['视频','功夫','创客','男篮','女篮','欧美足球','智慧冬奥','奥运会']:
                url = 'http://sports.sohu.com'+i.xpath('@href').get().strip()
                yield scrapy.Request(url=url,meta=meta,callback=self.parse_sports_1,dont_filter=False)


    def parse_sports_1(self,response):
        meta = response.meta
        json_url = response.xpath('//div[@id="feed-wrapper"]/@data-url').extract_first()
        pvid = re.search(r'window.sohuSpm._eCode = "(.*?)";',response.text).group(1)
        meta['channelId'] = re.search('/(\d+)\?',json_url).group(1)
        if not 'https:' in json_url:
            json_url = 'https:'+json_url
        json_url+='&page=1&pvId=%s'%(pvid)
        meta['pageNum'] = 1
        meta['pvid'] = pvid
        yield scrapy.Request(json_url,callback=self.parse_sports_2,meta=meta)


    def parse_sports_2(self,response):
        meta = response.meta
        data = json.loads(response.text)
        articles = data['data']
        if articles:
            for i in articles:
                url = 'https:'+i.get('url')
                meta['title'] = i.get('title')
                yield scrapy.Request(url,callback=self.get_content,meta=response.meta)
            meta['pageNum']+=1
            next_page = 'https://v2.sohu.com/integration-api/mix/region/{}?adapter=pc&page={}&pvId={}'.format(meta['channelId'],meta['pageNum'],meta['pvid'])
            yield scrapy.Request(url=next_page,meta=meta,callback=self.parse_sports_2)



    def parse_second_nav(self, response):
        meta = response.meta
        meta ['pgNum'] = 1
        thirdTag_nodes = response.xpath('//div[@class="second-nav"]/div[@ data-role="box"] |//div[@class="category-second-nav"]/div[contains(@class,"category-common") and position()>1]')
        for i in thirdTag_nodes:
            meta['third_tag'] = i.xpath('h4/a/text()').get().strip()
            url = i.xpath('h4/a/@href').get().strip()
            sceneId = re.search(r'/(\d*?)$', url).group(1)
            meta['sceneId'] = sceneId
            url = 'http://v2.sohu.com/public-api/feed?scene=CATEGORY&sceneId={}&page=2&size=20'.format(sceneId)
            yield scrapy.Request(url,meta=meta,callback=self.parse_json)

    def parse_json(self,response):
        meta = response.meta
        data = json.loads(response.text)
        if data:
            for i in data:
                authorId = i['authorId']
                id = i.get('id')
                title = i.get('title')
                if authorId and id and title:
                    meta['title'] = title.strip()
                    url = 'http://www.sohu.com/a/{}_{}'.format(id,authorId)
                    yield scrapy.Request(url=url,meta=meta,callback=self.get_content)
            meta['pgNum']+=1
            next_page = 'http://v2.sohu.com/public-api/feed?scene=CATEGORY&sceneId={}&page=2&size=20'.format(meta['sceneId'])
            yield scrapy.Request(url=next_page,meta=meta,callback=self.parse_json)





    def get_content(self, response):
        # print(response.body.decode('utf-8'))
        meta = response.meta
        item = JoviLonglasttimeItem()
        contents = response.xpath(
            '//*[@class="article"]/p[not(@data-role)]//text()|//*[@class="article-text"]/p//text()').extract()
        article_content = ''
        pattern = r'返回搜狐|原标题：|选自：|公众号|▲|文章来自|本文|来源|｜|来自网络|作者：|声明：|译自|如有侵权|\||编辑：|编者按|往期回顾|记者|点击进入|联合出品|【精彩推荐】|·|导读|导言：|导读：'
        for i in contents:
            if re.search(pattern, i):
                continue
            else:
                article_content += i.strip()
        item['article_content'] = article_content.replace('\r', '').replace('\n', '').replace('\t', '').replace(
            '\u3000', '').replace('\xa0', '')
        item['article_url'] = response.url
        item['article_title'] = meta['title']
        item['first_tag'] = meta['first_tag']
        item['second_tag'] = meta['second_tag']
        item['third_tag'] = meta['third_tag']
        yield item
