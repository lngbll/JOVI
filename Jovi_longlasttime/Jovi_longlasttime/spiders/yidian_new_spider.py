# -*- coding: utf-8 -*-
import json
import re
import time

import scrapy

from Jovi_longlasttime.items import JoviLonglasttimeItem


# 内容太少，搁置
class YidianNewSpiderSpider(scrapy.Spider):
    log_dir = 'e:\\日志文件夹\\JOVI新闻爬虫\\yidian_spider'
    date = time.strftime('%Y-%m-%d', time.localtime())
    name = 'yidian_new_spider'
    allowed_domains = ['www.yidianzixun.com']
    start_urls = ['https://www.yidianzixun.com/']
    meta = dict()
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'cookie': 'JSESSIONID=5e5dc4668c451edd49caf26f0d7cd69ace0974d7f3778c732dd81a8483cafc8c; wuid=145771195936444; wuid_createAt=2018-10-07 9:58:14; UM_distinctid=1664c3f1b73e6-00c5cc7c1bbeb6-2711639-1fa400-1664c3f1b7595e; weather_auth=2; Hm_lvt_15fafbae2b9b11d280c79eff3b840e45=1539072204,1539306476,1539738611,1539743665; CNZZDATA1255169715=1140288098-1538873369-null%7C1539739423; captcha=s%3A7e209d31746cd75ae2645b1aac9bfab9.daWbTl3KwMvrb4EhEonB6lSt%2FXkE%2FXZ%2BjkmQxQuoXtY; Hm_lpvt_15fafbae2b9b11d280c79eff3b840e45=1539743672; cn_1255169715_dplus=%7B%22distinct_id%22%3A%20%221664c3f1b73e6-00c5cc7c1bbeb6-2711639-1fa400-1664c3f1b7595e%22%2C%22sp%22%3A%20%7B%22%24_sessionid%22%3A%200%2C%22%24_sessionTime%22%3A%201539743667%2C%22%24dp%22%3A%200%2C%22%24_sessionPVTime%22%3A%201539743667%7D%7D',
        'pragma': 'no-cache',
        'referer': 'https://www.yidianzixun.com/channel/c3',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',

    }
    custom_settings = {
        'LOG_FILE': '{}\\{}.log'.format(log_dir, date),
        'REDIRECT_ENABLED': False,
        'DOWNLOADER_MIDDLEWARES': {
            # 'Jovi_longlasttime.middlewares.ProxyMiddleware': 300,
            'Jovi_longlasttime.middlewares.UaMiddleware': 400,
            'Jovi_longlasttime.middlewares.SeleniumMiddleware': 500,
            'Jovi_longlasttime.middlewares.redisMiddleware': 200
        },
        'ITEM_PIPELINES': {
            'Jovi_longlasttime.pipelines.BloomFilterPipeline': 200,
            'Jovi_longlasttime.pipelines.Duppipline': 300,
            # # 'Jovi_longlasttime.pipelines.Mongopipline': 400,   #默认不开启MongoDB,节省内存资源
            'Jovi_longlasttime.pipelines.To_csv1': 500
        }
    }

    def parse(self, response):
        meta = self.meta
        # json.loads的字符串中不能出现转义符
        file = json.loads(
            re.search(r'window\.yidian\.docinfo = (.*?)\n</script>', response.body.decode('utf-8'), re.S).group(
                1).replace('\\', ''))
        cate = file['user_info']['user_channels']
        for i in cate:
            meta['second_tag'] = i['name']
            if meta['second_tag'] not in ['首页', '图片', '一点号', '比赛', '美图', 'GIF图', '段子', '游戏', '动漫', '电台', '搞笑']:
                url = 'https://www.yidianzixun.com/channel/' + i['fromId']
                yield scrapy.Request(url=url, callback=self.get_url, meta=meta)

    def get_url(self, response):
        meta = response.meta
        urls = response.xpath('//div[@class="channel-news channel-news-0"]/a/@href').extract()
        for i in urls:
            if 'V_' not in i:
                url = 'https://www.yidianzixun.com' + i
                yield scrapy.Request(url, callback=self.get_content, meta=meta)

    def get_content(self, response):
        meta = response.meta
        item = JoviLonglasttimeItem()
        # doc_info = json.loads(re.search(r'window\.yidian\.docinfo = (.*?)\n</script>',response.body.decode('utf-8'),re.S).group(1).replace('\\',''))
        try:
            artical_contents = response.xpath('//div[@class="content-bd"]//p//text()').extract()
            content = ''
            pattern = r'图文|说明：|原标题|原题|选自：|公众号|▲|文章来自|本文|来源|｜|来自网络|作者：|声明：|译自|如有侵权|\||编辑|编者|往期回顾|记者|点击进入|联合出品|提示：|导语：|转载联系|责编'
            for i in artical_contents:
                if re.search(pattern, i, re.S):
                    continue
                else:
                    content += i.strip()
            item['article_content'] = content.replace('\r', '').replace('\t', '').replace('\n', '').replace('\xa0',
                                                                                                            '').replace(
                '\u3000', '')
            item['article_title'] = response.xpath('//h2/text()').extract_first().strip()
            item['first_tag'] = '一点资讯'
            item['second_tag'] = meta['second_tag']
            item['article_url'] = response.url
            yield item
        except AttributeError:
            print('页面跳转，无法抓取%s' % response.url)
        # try:
        #     item['source'] = response.xpath('//a[@class="doc-source"]/text()').extract_first()
        # except AttributeError:
        #     item['source'] = ''
        # try:
        #     item['update_time'] = response.xpath('//div[@class="meta"]/*[last()]/text()').extract_first()
        # except AttributeError:
        #     item['update_time'] = ''
