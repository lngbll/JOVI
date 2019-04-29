# -*- coding: utf-8 -*-
import json
import re
import scrapy
from Jovi_longlasttime.items import JoviLonglasttimeItem

"""
央视新闻各频道只开放前100条新闻，根据更新速度，可以看到昨天或者上星期的新闻，建议隔天开启爬虫，并一周汇总一次
"""


class CctvspiderSpider(scrapy.Spider):
    name = 'CCTV_spider'
    # allowed_domains = ['news.cctv.com']
    # start_urls = ['http://news.cctv.com/']
    meta = dict()
    category = {
        '国内': 'http://news.cctv.com/china/data/index.json',
        '国际': 'http://news.cctv.com/world/data/index.json',
        '军事': 'http://military.cctv.com/data/index.json',
        '科技': 'http://news.cctv.com/tech/data/index.json',
        '社会': 'http://news.cctv.com/society/data/index.json',
        '法治': 'http://news.cctv.com/law/data/index.json',
        '娱乐': 'http://news.cctv.com/ent/data/index.json',
        '经济': 'http://jingji.cctv.com/caijing/data/index.json',
        '评论': 'http://opinion.cctv.com/data/index.json',
        # 其中有几个板块人为的去掉了，因为这几个板块跳转到单独的网站，或者因为不适合作为新闻文章收录，加入会让脚本变复杂，其实也不缺这点数据
    }
    custom_settings = {
        'ITEM_PIPELINES' :{
            'Jovi_longlasttime.pipelines.Redispipline': 200,
            'Jovi_longlasttime.pipelines.Duppipline': 300,
            'Jovi_longlasttime.pipelines.To_csv1': 500
        },
    }
    def start_requests(self):
        meta = self.meta
        for k, v in self.category.items():
            meta['second_tag'] = k
            url = v
            yield scrapy.Request(url=url, meta=meta, callback=self.get_urls)

    def get_urls(self, response):
        meta = response.meta
        data = json.loads(response.text)
        articles = data['rollData']
        for article in articles:
            meta['title'] = article['title']
            url = article['url']
            yield scrapy.Request(url, meta=meta, callback=self.get_content)

    def get_content(self, response):
        meta = response.meta
        contents = response.xpath('//div[@class="cnt_bd"]/p[not(script)] | //div[@class="shizhendema_Aind_9810_2013120304"]/div[@class="bd"]/p[not(script)]').xpath('string()').extract()
        content = ''
        pattern = r'原标题：|原标题：'
        for i in contents:
            if re.search(pattern, i):
                continue
            else:
                content += i.strip()
        item = JoviLonglasttimeItem()
        item['article_title'] = meta['title']
        rep_content = 'var fo = createPlayer("v_player",540,400);fo.addVariable("videoId","vid");fo.addVariable("videoCenterId","bb13275ded2b46638e9ffc02983aaf38");fo.addVariable("videoType","0");fo.addVariable("videoEditMode","1");fo.addVariable("isAutoPlay","true");fo.addVariable("tai","news");fo.addVariable("languageConfig","");fo.addParam("wmode","opaque");writePlayer(fo,"embed_playerid");'
        item['article_content'] = content.replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0',
                                                                                                        '').replace(
            '\u3000', '').replace(rep_content,'')
        item['first_tag'] = '央视新闻'
        item['second_tag'] = meta['second_tag']
        item['article_url'] = response.url
        yield item
