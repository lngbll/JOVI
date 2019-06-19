# -*- coding: utf-8 -*-
import json
import re
from urllib.parse import urlparse

import scrapy
from scrapy.log import logger
from Jovi_longlasttime.items import JoviLonglasttimeItem
import time


class ZakerSpiderSpider(scrapy.Spider):
    log_dir = 'e:\\日志文件夹\\JOVI新闻爬虫\\Zaker_spider'
    date = time.strftime('%Y-%m-%d', time.localtime())
    name = 'Zaker_spider'
    allowed_domains = ['www.myzaker.com']
    start_urls = ['http://www.myzaker.com/']
    xpath = {
        'h5.ifeng.com':{
            'title':'//div[@class="tpl_header_title"]//text()',
            'ps':'//div[@class="tpl_main"]//p//text()'
        },
        'mobile2.itanzi.com': {
            'title': '//*[@class="post-title"]//text()',
            'ps': '//*[@class="post-page-content"]//p//text()'
        },
        'www.happyjuzi.com': {
            'title': '//*[@class="title"]/text()',
            'ps': '//article//p//text()'
        },
        'www.thetigerhood.com': {
            'title': '//*[@id="jsArticleTitle"]/text() | //*[@class="entry-header"]/h1/text()',
            'ps': '//article/*[@class="entry-content"]//p//text() | //*[@class="entry-content"]//p//text()'
        },
        'm.vogue.com.cn': {
            'title':'//div[@class="tpl_header_title"]//text()',
            'ps':'//div[@class="tpl_main"]//p//text()'
        },
        'www.stylemode.com': {
            'title': '//article//h1/text()',
            'ps': '//article//*[@id="article-content"]//p//text()'
        },
        'inveno.nanrenwo.net': {
            'title': '//*[@class="i-m-title i-s-bold"]//text()',
            'ps': '//*[@class="i-m-content"]//p//text()'
        },
        'www.xbiao.com': {
            'title': '//*[@class="title"]//h1//text()',
            'ps': '//*[@class="article"]//p//text()'
        },
        'cul.qq.com': {
            'title': '//*[@class="hd"]/h1/text()',
            'ps': '//*[@class="Cnt-Main-Article-QQ"]//p[@style="TEXT-INDENT: 2em"]//text()'
        },
        'sp.zhids.cn': {
            'title': '//*[@id="Lab_Title"]/text()',
            'ps': '//*[@id="HtmlContent"]//p[@style="text-align: center; line-height: 1.75em;"]//text()'
        },
        'fashion.sina.com.cn': {
            'title': '//*[@class="main-title"]/text()',
            'ps': '//*[@id="artibody"]//p//text()'
        },
        'www.myzaker.com': {
            'title': '//*[@class="article_header"]/h1/text()',
            'ps': '//*[@id="content"]//p//text()'
        },
        'rss1.thehour.cn':{
            'title':'//*[@class="tpl_header_title"]/text()',
            'ps':'//*[@class="tpl_main"]//p//text()'
        },
        'news.qq.com': {
            'title': '//*[@class="hd"]/h1/text()',
            'ps': '//*[@id="Cnt-Main-Article-QQ"]//p//text()'
        },
        'www.xiachufang.com':{
            'title':'//*[@class="page-title"]/text()',
            'ps':'//*[@class="block recipe-show"]//text()'
        },
        'm.haibao.com': {
            'title': '//*[@id="jsArticleTitle"]/text()',
            'ps': '//*[@class="block recipe-show"]//text()'
        },
        'mp.weixin.qq.com': {
            'title': '//*[@id="activity-name"]/text()',
            'ps': '//*[@id="js_content"]//span//text()'
        },
        'm.bazaar.com.cn': {
            'title': '//*[@class="art-hd"]/h1/text()',
            'ps': '//*[@class="art-body"]//p//text()'
        },
        'www.cankaoxiaoxi.com': {
            'title': '//*[@class="articleHead"]/h1/text()',
            'ps': '//*[@class="articleText"]//p//text()'
        },
        'dress.pclady.com.cn':{
            'title':'//*[@class="artCon"]/h1/text()',
            'ps':'//*[@id="artText"]//p//text()'
        }
    }
    meta = {
        'first_tag': 'Zaker新闻',
        'second_tag': '',
        'third_tag': '',
        'title': '',
        'page_num': 1

    }
    custom_settings = {
        'LOG_FILE':'{}\\{}.log'.format(log_dir,date),
        'ITEM_PIPELINES': {
            'Jovi_longlasttime.pipelines.BloomFilterPipeline': 200,
            'Jovi_longlasttime.pipelines.Duppipline': 300,
            # # # 'Jovi_longlasttime.pipelines.Mongopipline': 400,   #默认不开启MongoDB,节省内存资源
            'Jovi_longlasttime.pipelines.To_csv1': 500
        },
        'DOWNLOAD_DELAY':0.5
    }


    def parse(self,response):
        meta = self.meta
        second_tag_node = response.xpath('//div[@class="nav"]/a | //div[@class="nav_menu"]/a')
        for i in second_tag_node:
            meta['second_tag'] = i.xpath('text()').extract_first().strip()
            url = i.xpath('@href').extract_first()
            yield scrapy.Request(url='http:'+url,meta=meta,callback=self.get_first_page)


    def get_first_page(self,response):
        meta = response.meta
        article_urls = response.xpath('//div[@id="section"]//a/@href').extract_first()
        for i in article_urls:
            yield scrapy.Request('http:'+i,meta=meta,callback=self.get_content)
        first_page = response.xpath('//input[@id="nexturl"]/@value').extract_first()
        url = 'http:'+first_page
        yield scrapy.Request(url,meta=meta,callback=self.get_url)

    def get_url(self, response):
        meta = response.meta
        data = json.loads(response.text)
        try:
            for i in data['data']['article']:
                url = i['href']
                yield scrapy.Request(url='http:' + url, callback=self.get_content, meta=meta)
            if 'next_url' in data['data'].keys():
                meta['page_num'] += 1
                yield scrapy.Request(url='http:' + data['data']['next_url'], callback=self.get_url, meta=meta)
        except KeyError:
            print('网页格式有变化，注意更改脚本')


    def get_content(self, response):
        meta = response.meta
        item = JoviLonglasttimeItem()
        item['article_url'] = response.url
        item['first_tag'] = meta['first_tag']
        item['second_tag'] = meta['second_tag']
        host = urlparse(response.url).netloc
        xpath = self.xpath.get(host)
        if xpath:
            item['article_title'] = response.xpath(xpath['title']).get().strip()
            ps = response.xpath(xpath['ps']).getall()
        else:
            logger.info('This URL parsing xpath is not settled:{}'.format(response.url))
            print(response.url)
            return
        content = ''
        for p in ps:
            if re.search(r'责任编辑：|作者：|出处：|{}|来自：|来源 :|来源：|来源 : |图片来自|图片由|图：|更多精彩|请投稿至：|文|文／|编辑',p):
                continue
            elif re.search(r'关注微信公众号|参考资料|声明：|原网页已经由 ZAKER 转码排版 |推荐阅读', p):
                break
            else:
                content += p.strip()
        item['article_content'] = content.replace('\n', '').replace('\r', '').replace('\t', '').replace('\u3000','').replace('\xa0', '')
        yield item
