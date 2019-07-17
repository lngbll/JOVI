# -*- coding: utf-8 -*-
import scrapy
import json
import re
import time
from Jovi_longlasttime.items import JoviLonglasttimeItem
"""
手机版凤凰网内容太少，还是爬网页版
"""


class FenghuangSpiderSpider(scrapy.Spider):
    name = 'fenghuang_spider'

    log_dir = 'e:\\日志文件夹\\JOVI新闻爬虫\\fenghuang_spider'
    date = time.strftime('%Y-%m-%d', time.localtime())


    allowed_domains = ['www.ifeng.com']
    start_urls = ['http://www.ifeng.com/']
    channels = {
        '财经': {
            '全球财经速报': 'http://finance.ifeng.com/shanklist/1-66-',
            '证券': 'http://finance.ifeng.com/shanklist/1-62-',
            '炒股大赛': 'https://finance.ifeng.com/shanklist/1-67-',
            '港股': 'http://finance.ifeng.com/shanklist/1-69-',
            'wemoney': 'http://finance.ifeng.com/shanklist/1-74-'

        },
        '娱乐': {
            '明星': 'http://ent.ifeng.com/star/',
            '电影': 'http://ent.ifeng.com/movie/',
            '电视': 'http://ent.ifeng.com/tv/',
            '音乐': 'http://ent.ifeng.com/music/',
        },
        '体育': {
            '中国足球': 'http://sports.ifeng.com/zgzq/',
            '国际足球': 'http://sports.ifeng.com/gjzq/',
            'NBA': 'http://sports.ifeng.com/nba/',
            'CBA': 'http://sports.ifeng.com/zglq/',
            '综合体育': 'http://sports.ifeng.com/zhty/',

        },
        '文化读书': {
            '文化资讯': 'http://culture.ifeng.com/shanklist/17-35104-',
            '洞见': 'http://culture.ifeng.com/shanklist/17-35105-',
            '读书': 'http://culture.ifeng.com/shanklist//17-35108-',
        },
        '军事': {
            '军情热点': 'http://mil.ifeng.com/shanklist/14-35083-',
            '凤凰军评': 'http://mil.ifeng.com/shanklist/original/14-35085-',
            '战争历史': 'http://mil.ifeng.com/shanklist/14-35086-',
        },
        '历史': {
            '热文': 'http://history.ifeng.com/shanklist/15-35075-',
            '兰台说史': 'http://history.ifeng.com/shanklist/original/15-35076-',
        },
        '科技': {
            '数码': 'http://tech.ifeng.com/digi/',
            '手机': 'http://tech.ifeng.com/mobile/',
            '风眼': 'http://tech.ifeng.com/core/',
            '凤凰评测': 'http://tech.ifeng.com/lab/',
            '深度阅读': 'http://tech.ifeng.com/profound/',
            '区块链': 'http://tech.ifeng.com/blockchain/',

        },
        '时尚': {
            '时装': 'http://fashion.ifeng.com/trends/',
            '美容': 'http://fashion.ifeng.com/beauty/',
            '奢侈品': 'http://fashion.ifeng.com/luxury/',
            '生活': 'http://fashion.ifeng.com/lifestyle/',
            '情感': 'http://fashion.ifeng.com/emotion/',
        },
        '旅游': {
            '旅游资讯': 'https://travel.ifeng.com/shanklist/33-60139-',
            # '旅游住宿': 'https://travel.ifeng.com/listpage/17179/1/list.shtml',
            '爱上路': 'https://travel.ifeng.com/shanklist/33-60146-',
            '游物': 'https://travel.ifeng.com/shanklist/33-60147-',
        },
        '佛教': {
            '佛教常识': 'https://fo.ifeng.com/listpage/126/1/list.shtml',
            '资讯': 'https://fo.ifeng.com/listpage/119/1/list.shtml',
            '般若讲堂': 'https://fo.ifeng.com/listpage/8605/1/list.shtml',
            '佛教故事': 'https://fo.ifeng.com/listpage/8537/1/list.shtml',
            '佛教公益': 'https://fo.ifeng.com/listpage/8542/1/list.shtml',
            '智慧法语': 'https://fo.ifeng.com/listpage/8541/1/list.shtml',
            '佛教观察家': 'https://fo.ifeng.com/listpage/8541/1/list.shtml',
            '素食茶禅': 'https://fo.ifeng.com/listpage/8557/1/list.shtml'

        },
        '政务': {
            '要闻': 'https://gov.ifeng.com/shanklist/22-35141-',
            '高层动态': 'https://gov.ifeng.com/shanklist/22-35142-',
            '政策': 'https://gov.ifeng.com/shanklist/22-35143-',
            '人事': 'https://gov.ifeng.com/shanklist/22-35144-',
            '地方': 'https://gov.ifeng.com/shanklist/22-35145-',
            '发展治理': 'https://gov.ifeng.com/shanklist/22-35146-',
            '防腐': 'https://gov.ifeng.com/shanklist/22-35147-',
            '环保': 'https://gov.ifeng.com/shanklist/22-35148-',
            '文旅': 'https://gov.ifeng.com/shanklist/22-35149-',
            '合作': 'https://gov.ifeng.com/shanklist/22-35150-'
        },
        '电竞': {
            'LOL': 'http://games.ifeng.com/listpage/17257/1/list.shtml',
            'DOTA2': 'http://games.ifeng.com/listpage/17258/1/list.shtml',
            'CS-GO': 'http://games.ifeng.com/listpage/27365/1/list.shtml',
            '移动电竞': 'http://games.ifeng.com/listpage/27312/1/list.shtml',
            '电竞综合': 'http://games.ifeng.com/listpage/17889/1/list.shtml',

        },
        '国学': {
            '热文': 'https://guoxue.ifeng.com/shanklist/20-35097-',
            '国学大典': 'https://guoxue.ifeng.com/shanklist/20-35097-',
            '国学大讲坛': 'https://guoxue.ifeng.com/shanklist/original/20-35098-',
            '非常国学课': 'https://guoxue.ifeng.com/shanklist/20-35101-'
        },
        '养生': {
            '养生': 'http://health.ifeng.com/shanklist/12-35223-',
            '美食': 'http://health.ifeng.com/shanklist/12-35224-',
            '两性': 'http://health.ifeng.com/shanklist/12-35227-',
            '健身': 'http://health.ifeng.com/shanklist/12-35225-',
            '母婴': 'http://health.ifeng.com/shanklist/12-35226-',
            '电商': 'http://health.ifeng.com/shanklist/12-35228-',
        },
        '酒业': {
            '酒闻播报': 'https://jiu.ifeng.com/listpage/15843/1/list.shtml',
            '大佬酒评': 'https://jiu.ifeng.com/listpage/15844/1/list.shtml',
            '焦点时刻': 'https://jiu.ifeng.com/listpage/15845/1/list.shtml',
            '市场调研': 'https://jiu.ifeng.com/listpage/15846/1/list.shtml',
            '酒典': 'https://jiu.ifeng.com/listpage/15859/1/list.shtml',
            '品鉴': 'https://jiu.ifeng.com/listpage/15860/1/list.shtml',
            '酒股快报': 'https://jiu.ifeng.com/listpage/15855/1/list.shtml',
        }
    }
    meta = dict()
    json_request_pattern = 'http://shankapi.ifeng.com/shanklist/_/getColumnInfo/_/default/{}/{}/20/{}'
    custom_settings = {
        'LOG_LEVEL':'INFO',
        'LOG_FILE': '{}\\{}.log'.format(log_dir, date),
        'REDIRECT_ENABLED':False
    }

    def start_requests(self):
        meta = self.meta
        for j,k in self.channels.items():
            meta['second_tag'] = j
            for m,n in k.items():
                meta['third_tag'] = m
                if 'listpage' not in n:
                    yield scrapy.Request(url=n,callback=self.get_str_url,meta=meta)
                else:
                    yield scrapy.Request(url=n,callback=self.get_html_url,meta=meta)

    # 解析以html形式的urls
    def get_html_url(self,response):
        meta = response.meta
        nav = response.xpath('//div[@class="fl main"]//a | //div[@id="box_content"]//h2/a | //div[@class="box650"]//h2/a | //div[@class="zx_list"]//h1/a')
        next_page = response.xpath('//a[contains(text(),"下一页")]')
        for i in nav:
            meta['title'] = i.xpath('text()').extract_first().strip()
            url = i.xpath('@href').extract_first()
            yield scrapy.Request(url=url, callback=self.get_content, meta=meta, dont_filter=True)
        if next_page:
            next_request_url = next_page.xpath('@href').extract_first()
            yield scrapy.Request(url=next_request_url,callback=self.get_html_url,meta=meta)


    # 解析javascript方式的urls
    def get_str_url(self,response):
        meta = response.meta
        allData = re.search('var allData = (.*?);\n',response.text).group(1)
        data = json.loads(allData)
        columnId = data['columnId']
        meta['columnId'] = columnId
        newsstream = data['newsstream']
        next_request_id = newsstream[-1]['id']
        next_request_tp = 1000*time.mktime(time.strptime(newsstream[-1]['newsTime'],"%Y-%m-%d %H:%M:%S"))
        next_request = self.json_request_pattern.format(next_request_id,next_request_tp,columnId)
        isEnd = data['isEnd']
        if not isEnd:
            yield scrapy.Request(url=next_request,callback=self.get_json_url,meta=meta,dont_filter=True)
        for news in newsstream:
            meta['title'] = news['title']
            url = news['url']
            yield scrapy.Request(url=url,callback=self.get_content,meta=meta,dont_filter=True)

    # 解析json形式的urls
    def get_json_url(self,response):
        meta = response.meta
        allData = json.loads(response.text)
        data = allData['data']
        isEnd = data['isEnd']
        newsstream= data['newsstream']
        next_request_id = newsstream[-1]['id']
        next_request_tp = 1000 * time.mktime(time.strptime(newsstream[-1]['newsTime'], "%Y-%m-%d %H:%M:%S"))
        columnId = meta['columnId']
        next_request = self.json_request_pattern.format(next_request_id, next_request_tp, columnId)
        if not isEnd:
            yield scrapy.Request(url=next_request,callback=self.get_json_url,meta=meta,dont_filter=True)
        for news in newsstream:
            type = news['type']
            meta['title'] = news['title']
            url = news['url']
            if type == 'article':
                yield scrapy.Request(url=url, callback=self.get_content, meta=meta,dont_filter=True)

    def get_content(self,response):
        meta = response.meta
        item = JoviLonglasttimeItem()
        pattern = r'http[s]*://[\S]+.ifeng.com/a/[\d]{8}/[\d]+_0.[s]*html'
        # 两种形式的url,提取规则不一样
        if re.search(pattern,response.url):
            contents = response.xpath('//div[@id="main_content"]/p//text()').extract()
        else:
            try:
                allData = re.search('var allData = (.*?);\n', response.text).group(1)
                allData = json.loads(allData)
                docData = allData['docData']
                type = docData['contentData']['contentList'][-1]['type']
                if type=='text':
                    contentData = docData['contentData']['contentList'][-1]['data']
                    contents = scrapy.Selector(text=contentData).xpath('//p[not(@class)]//text()').extract()
                else:
                    contents = []
                    print('内容是视频或者图片----%s' % response.url)
            except Exception as e:
                print('可能发生跳转或者没有内容----%s' % response.url)
                print(e)
                contents =[]
        pattern1 = r'编辑：|注：|关注(.*?)公众号|作者:|请关注|微信号：|本文为|未经授权|作者原创|微信公号：|微信ID：|作者简介：|原标题：|记者｜|编辑｜|来源：'
        content = ''
        for i in contents:
            if re.search(pattern1,i):
                continue
            elif re.search(r'- END -|END',i):
                break
            else:
                content += i.strip()
        item['first_tag'] = '凤凰网'
        item['second_tag'] = meta['second_tag']
        item['third_tag'] = meta['third_tag']
        item['article_url'] = response.url
        item['article_title'] = meta['title']
        item['article_content'] = content.replace('\r','').replace('\n','').replace('\t','').replace('\xa0','').replace('\u3000','')
        yield item


