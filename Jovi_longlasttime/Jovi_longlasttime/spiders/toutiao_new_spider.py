# -*- coding: utf-8 -*-
import re,time
import redis
from lxml import etree

import scrapy
from scrapy import log
from Jovi_longlasttime.items import JoviLonglasttimeItem




class ToutiaoNewSpiderSpider(scrapy.Spider):
    name = 'toutiao_new_spider'
    # allowed_domains = ['']
    log_dir = 'e:\\日志文件夹\\JOVI新闻爬虫\\toutiao_new_spider'
    date = time.strftime('%Y-%m-%d', time.localtime())
    meta = {
        'first_tag': '今日头条',
        'second_tag': '',
        'title': '',
    }
    HTML_entity = {
        r'\"':'"',
        r"\u003C": "<",
        r"\u003E": ">",
        r"\u002F": "/",
        "&nbsp;": " ",
        "&lt;": "<",
        "&gt;": ">",
        "&amp;": "&",
        "\&quot;": r'"',
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
        res = response.text
        item = JoviLonglasttimeItem()
        content = re.search(r' content: \'(.*?)\'.slice\(6, -6\),', res)
        title = re.search(r' title: \'(.*?)\'.slice\(6, -6\),',res)
        second_tag = re.search(r'chineseTag: \'(.*?)\',',res)
        if content:
            content = content.group(1)[6:-6]
        else:
            log.msg('此URL没有文章----%s'%response.url,level=log.INFO)
            return
        if title:
            title = title.group(1)[6:-6]
            # log.msg(response.url,level=log.INFO)
        else:
            log.msg('此URL没有标题----%s'%response.url,level=log.INFO)
            return
        if second_tag:
            second_tag=second_tag.group(1)
        else:
            log.msg('此URL没有二级标签----%s'%response.url,level=log.INFO)
            return
        for k,j in self.HTML_entity.items():
            content = content.replace(k,j)
        # print(content)
        e = etree.HTML(content).xpath('//p//text()')
        pattern = r"图片来自|原标题：|选自：|公众号|▲|文章来自|本文|来源|｜|来自网络|作者：|声明：|译自|如有侵权|\||责任编辑：|编者按|往期回顾|记者|点击进入|联合出品|【精彩推荐】|·|责编|源丨|文丨|转载联系"
        article = ''
        for i in e:
            if re.search(pattern,i):
                continue
            else:
                article+=i.strip()
        article = article.replace('\r', '').replace('\n', '').replace('\t', '').replace(
                '\xa0', '').replace('\u3000', '').replace('\u200b', '')
        item['article_content'] = article
        item['article_title'] =title
        item['first_tag'] = meta['first_tag']
        item['second_tag'] = second_tag
        item['article_url'] = response.url
        yield item






