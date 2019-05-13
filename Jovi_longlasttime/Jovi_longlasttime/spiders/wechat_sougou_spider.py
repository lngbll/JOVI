# -*- coding: utf-8 -*-

import re
import time
import scrapy

from Jovi_longlasttime.items import JoviLonglasttimeItem
"""
    搜狗微信只保留了一天到两天的内容，因此改成日更新。
"""




class WechatSougouSpiderSpider(scrapy.Spider):
    name = 'wechat_sougou_spider'
    start_urls = ['http://weixin.sogou.com/']
    log_dir = 'e:\\日志文件夹\\JOVI新闻爬虫\\搜狗微信_spider'
    date = time.strftime('%Y-%m-%d', time.localtime())
    meta = {
        'third_tag': '',
        'meta': ''
    }
    channels = ['热门', '搞笑', '养生堂', '私房话', '八卦金', '科技咖', '财经迷', '汽车控', '生活家', '时尚圈', '育儿', '旅游',
                '职场', '美食', '历史', '教育', '星座', '体育', '军事', '游戏', '萌宠']
    custom_settings = {
        'LOG_FILE':'{}\\{}.log'.format(log_dir,date),
        'ITEM_PIPELINES': {
            'Jovi_longlasttime.pipelines.Redispipline': 200,
            'Jovi_longlasttime.pipelines.Duppipline': 300,
            # # 'Jovi_longlasttime.pipelines.Mongopipline': 400,   #默认不开启MongoDB,节省内存资源
            'Jovi_longlasttime.pipelines.To_csv1': 500
        },
        'DOWNLOAD_DELAY':1

    }

    def parse(self, response):
        meta = self.meta
        for i in range(1, len(self.channels)):
            meta['third_tag'] = self.channels[i]
            for j in range(5):
                if j == 0:
                    url = 'https://weixin.sogou.com/pcindex/pc/pc_%d/pc_%d.html' % (i, i)
                else:
                    url = 'https://weixin.sogou.com/pcindex/pc/pc_%d/%d.html' % (i, j)
                yield scrapy.Request(url, callback=self.get_url, meta=meta)

    def get_url(self, response):
        meta = response.meta
        urls = response.xpath('//li//h3/a/@href').extract()
        for url in urls:
            url = url.replace('http', 'https')
            yield scrapy.Request(url, callback=self.get_content, meta=meta)

    def get_content(self, response):
        try:
            meta = response.meta
            item = JoviLonglasttimeItem()
            contents = response.xpath('//div[@id="js_content"]//p').xpath('string()').extract()
            content = ''
            pattern = r'点击[上下]方|关注(.*?)公众号|关注(.*?)微信|↓|原文|相关阅读|原文|说明：|原标题|原题|选自：|公众号|▲|文章来自|本文|来源|｜|来自网络|作者：|声明：|译自|如有侵权|\||编辑|编者|往期回顾|记者|点击进入|提示：|导语：|转载联系|责编'
            for i in contents:
                if re.search(pattern, i):
                    continue
                else:
                    content += i.strip()
            item['first_tag'] = '搜狗微信'
            item['second_tag'] = meta['third_tag']
            item['article_url'] = response.url
            item['article_title'] = response.xpath('//*[@id="activity-name"]/text()').extract_first().strip()
            item['article_content'] = content.replace('\r', '').replace('\t', '').replace('\n', '').replace('\xa0',
                                                                                                            '').replace(
                '\u3000', '')
            yield item
        except Exception:
            print('请求异常----%s' % response.url)
