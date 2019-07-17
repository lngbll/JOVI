# -*- coding: utf-8 -*-
import scrapy
import time
import re
from urllib.parse import urlparse

from Jovi_longlasttime.items import JoviLonglasttimeItem
class RenmingwangSpiderSpider(scrapy.Spider):
    name = 'renmingwang_spider'
    # allowed_domains = ['www.rengming.com']
    start_urls = ['http://www.people.com.cn/sitemap_index.xml']
    date = time.strftime('%Y-%m-%d', time.localtime())
    log_dir = 'e:\\日志文件夹\\JOVI新闻爬虫\\人民网'
    custom_settings = {
        "ITEM_PIPELINES":{
            'Jovi_longlasttime.pipelines.Duppipline':100,
            'Jovi_longlasttime.pipelines.BloomFilterPipeline':200,
            'Jovi_longlasttime.pipelines.To_csv1': 500
        },
        'DOWNLOADER_MIDDLEWARES':{},
        # 'LOG_LEVEL':'DEBUG',
        # 'LOG_FILE':'{}\{}.json'.format(log_dir,date)
    }

    channels = {
        'hn.people.com.cn':'国内',
        'it.people.com.cn':'IT',
        'gx.people.com.cn':'国内',
        'ah.people.com.cn':'国内',
        'art.people.com.cn': '书画',
        'auto.people.com.cn': '汽车',
        'bj.people.com.cn': '国内',
        'book.people.com.cn': '读书',
        'caipiao.people.com.cn': '彩票',
        'ccnews.people.com.cn': '央企',
        'cpc.people.com.cn': '时政',
        'cppcc.people.com.cn': '时政',
        'culture.people.com.cn': '文化',
        'dangjian.people.com.cn': '时政',
        'edu.people.com.cn': '教育',
        'energy.people.com.cn': '能源',
        'ent.people.com.cn': '娱乐',
        'env.people.com.cn': '环保',
        'finance.people.com.cn': '财经',
        'game.people.com.cn': '游戏',
        'gd.people.com.cn': '国内',
        'gongyi.people.com.cn': '公益',
        'gs.people.com.cn': '国内',
        'gz.people.com.cn': '国内',
        'hb.people.com.cn': '国内',
        'he.people.com.cn': '国内',
        'health.people.com.cn': '健康',
        'hi.people.com.cn': '国内',
        'history.people.com.cn': '历史',
        'hm.people.com.cn': '国内',
        'homea.people.com.cn': '家电',
        'hongmu.people.com.cn': '红木',
        'house.people.com.cn': '房产',
        'ip.people.com.cn': '知识产权',
        'japan.people.com.cn': '国际',
        'jl.people.com.cn': '国内',
        'js.people.com.cn': '国内',
        'jx.people.com.cn': '国内',
        'lady.people.com.cn': '时尚',
        'leaders.people.com.cn': '时政',
        'legal.people.com.cn': '法治',
        'media.people.com.cn': '传媒',
        'military.people.com.cn': '军事',
        'money.people.com.cn': '金融',
        'nm.people.com.cn': '国内',
        'npc.people.com.cn': '时政',
        'nx.people.com.cn': '国内',
        'opinion.people.com.cn': '观点',
        'picchina.people.com.cn': '图说中国',
        'politics.people.com.cn': '时政',
        'qh.people.com.cn':'国内',
        'renshi.people.com.cn': '时政',
        'ru.people.com.cn': '国际',
        'sc.people.com.cn': '国内',
        'scitech.people.com.cn': '科技',
        'sd.people.com.cn': '国内',
        'sh.people.com.cn': '国内',
        'shipin.people.com.cn': '食品',
        'sn.people.com.cn': '国内',
        'society.people.com.cn': '社会',
        'sports.people.com.cn':'体育',
        'sx.people.com.cn': '国内',
        'sz.people.com.cn': '国内',
        'tc.people.com.cn': '通信',
        'theory.people.com.cn': '理论',
        'tj.people.com.cn': '国内',
        'travel.people.com.cn': '旅游',
        'tw.people.com.cn': '台湾',
        'uk.people.com.cn': '国际',
        'unn.people.com.cn': '国内',
        'usa.people.com.cn': '国际',
        'world.people.com.cn': '国际',
        'www.womenvoice.cn': '女性',
        'xj.people.com.cn': '国内',
        'xz.people.com.cn': '国内',
        'yn.people.com.cn':'国内',
        'yuqing.people.com.cn': '舆情',
        'zj.people.com.cn': '国内',
    }

    def parse(self,response):
        urls = re.findall(r'<loc>(.*?)</loc>',response.text)
        for i in urls:
            yield scrapy.Request(url=i,callback=self.get_url_list,)

    def get_url_list(self,response):
        urls = re.findall(r'<loc>(.*?)</loc>',response.text)
        for i in urls:
            yield scrapy.Request(url=i,callback=self.get_content,)

    def get_content(self,response):
        item = JoviLonglasttimeItem()
        item['article_url'] = response.url
        item['first_tag'] = '人民网'
        item['second_tag'] = self.channels.get(urlparse(response.url).netloc)
        item['article_title'] = response.xpath('//h1/text()').get()
        xpath = '//*[@id="rwb_zw"]//p//text() | //*[@class="box_con"]//p//text() |' \
                ' //*[@class="box_con w1000 clearfix"]//p//text() | ' \
                '//*[@class="content clear clearfix"]//p//text() |' \
                '//*[@class="show_text"]//p//text() |' \
                '//*[@id="p_content"]//p//text() |' \
                '//*[@class="artDet"]//p//text() |' \
                '//*[@class="text"]//p//text() |' \
                '//*[@class="text width978 clearfix"]//p//text() |' \
                '//*[@id="zoom"]//p//text() |' \
                '//*[@class="text_show"]//p//text()'
        item['article_content'] = ''.join(map((lambda x:x.strip()),response.xpath(xpath).getall()))
        yield item


