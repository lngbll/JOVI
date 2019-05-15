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
    cat = ['娱乐', '汽车', '体育', '科技', '国内', '国际', '财经', '互联网', '军事', '游戏', '旅游', '教育', '时尚', '动漫',  '美食', '社会', '政务',
           '母婴', '宠物', '文化', '历史']
    meta = {
        'first_tag': '',
        'second_tag': '',
        'third_tag': '',
        'title': '',
    }
    custom_settings = {
        'LOG_file':'{}\\{}.log'.format(log_dir,date),
        # 'DEPTH_PRIORITY':1,
        'START_DIR': 'e:\搜狐网',
        'ITEM_PIPELINES':{
            'Jovi_longlasttime.pipelines.Redispipline': 200,
            'Jovi_longlasttime.pipelines.Duppipline': 300,
            'Jovi_longlasttime.pipelines.To_csv': 500
    }
    }

    def parse(self, response):
        meta = self.meta
        firstTag_nodes = response.xpath('//*[@class="navigation-top-wrapper"]/ul//a')
        for i in firstTag_nodes:
            firstTag = i.xpath('text()').extract_first()
            print('开始爬一级模块——%s' % firstTag)
            meta['first_tag'] = firstTag
            if meta['first_tag'] == '汽车':
                url = 'http://www.sohu.com/c/18'
                meta['first_tag'] = '汽车自媒体'  # 这个版块又变得和其他版块一样了
                yield scrapy.Request(url=url, callback=self.get_nav, meta=meta,dont_filter=True)
            elif meta['first_tag'] == '新闻':
                url = 'http://www.sohu.com/c/8'  # 这个版块又变得和其他版块一样了
                yield scrapy.Request(url=url, callback=self.get_nav, meta=meta,dont_filter=True)
            elif meta['first_tag'] == '体育':
                url = 'https://sports.sohu.com/' #体育板块连接
                yield scrapy.Request(url,callback=self.parse_sports,meta=meta,dont_filter=True)
            elif meta['first_tag']=='文化':
                url = 'http://cul.sohu.com/category/reading'
                yield scrapy.Request(url=url,callback=self.get_nav,meta=meta,dont_filter=True)
            elif meta['first_tag'] == '历史':
                url = 'http://history.sohu.com/1336'
                yield scrapy.Request(url=url,callback=self.get_nav,meta=meta,dont_filter=True)
            elif meta['first_tag'] =='科技':
                url = 'http://it.sohu.com/911'
                yield scrapy.Request(url=url,callback=self.get_nav,meta=meta,dont_filter=True)
            elif meta['first_tag'] not in ['搜狐', '更多','专题','房产']:
                url =i.xpath('@href').extract_first()
                if not 'http:' in url:
                    url = 'http:'+url
                yield scrapy.Request(url=url, callback=self.get_nav, meta=meta, dont_filter=True)


    def parse_sports(self,response):
        meta = response.meta
        second_tag_nodes = response.xpath('//div[@class="sports-navs"]//a[@class="link-txt"]')
        meta['second_tag'] = '体育'
        for i in second_tag_nodes:
            meta['third_tag'] = i.xpath('@data-link-name').extract_first()
            if meta['third_tag'] not in ['视频','功夫','创客','男篮','女篮','欧美足球','智慧东奥','奥运会']:
                yield scrapy.Request(second_tag_nodes.xpath('@href').extract_first(),meta=meta,callback=self.parse_sports_1,dont_filter=True)


    def parse_sports_1(self,response):
        meta = response.meta
        json_url = response.xpath('//div[@id="feed-wrapper"]/@data-url').extract_first()
        pvid = re.search(r'window.sohuSpm._eCode = "(.*?)";',response.text).group(1)
        if not 'https:' in json_url:
            json_url = 'https:'+json_url
        json_url+='&page=1&pvId=%s&_=%s'%(pvid,int(1000*time.time()))
        meta['page'] = 1
        meta['pvid'] = pvid
        yield scrapy.Request(json_url,callback=self.parse_sports_2,meta=meta,dont_filter=True)


    def parse_sports_2(self,response):
        response.meta['page']+=1
        data = json.loads(response.text)
        if data['data']:
            url = data['data']['url']
            if not 'https:' in url:
                url = 'https:'+url
            yield scrapy.Request(url,callback=self.get_content,meta=response.meta,)



    def get_nav(self, response):
        meta = response.meta
        secondTag_nodes = response.xpath('//div[@class="second_nav"]/div[position()>1]')
        if secondTag_nodes:
            for i in secondTag_nodes:
                meta['second_tag'] = i.xpath('*[1]/a/text()').extract_first()
                thirdTag_nodes = i.xpath('*[position()>1]/a')
                if thirdTag_nodes:
                    for j in thirdTag_nodes:
                        meta['third_tag'] = j.xpath('text()').extract_first()
                        url = j.xpath('@href').extract_first()
                        url = 'http://v2.sohu.com/public-api/feed?scene=TAG&sceneId={}&page=1&size=100'.format(
                            url.split('/')[-1])
                        yield scrapy.Request(url, callback=self.get_urls, meta=meta)
                else:
                    meta['third_tag'] = meta['second_tag']
                    url = i.xpath('//a/@href').extract_first()
                    url = 'http://v2.sohu.com/public-api/feed?scene=CAYEGORY&sceneId={}&page=1&size=100'.format(
                        url.split('/')[-1])
                    yield scrapy.Request(url=url, callback=self.get_content, meta=meta)
        else:
            meta['second_tag'] = '热点'
            thirdTag_nodes = response.xpath('//*[@data-role="left-hot-spots"]/*[position()>1]//a')
            for i in thirdTag_nodes:
                meta['third_tag'] = i.xpath('text()').extract_first()
                url = i.xpath('@href').extract_first()
                url = 'http://v2.sohu.com/public-api/feed?scene=TAG&sceneId={}&page=1&size=100'.format(
                    url.split('/')[-1])
                yield scrapy.Request(url, callback=self.get_urls, meta=meta)

                # 翻页专用回调函数

    def get_page(self, response):
        meta = response.meta
        pageNum = int(response.xpath('//*[@class="page"]/a[last()-2]/text()').extract_first())
        for i in range(1, pageNum + 1):
            url = 'http://baike.focus.cn/f_xuanershoufang_p{}/'.format(i)
            yield scrapy.Request(url=url, callback=self.get_urls, meta=meta, dont_filter=True)

    def get_urls(self, response):
        meta = response.meta
        if meta['first_tag'] == '体育':
            meta['second_tag'] = '滚动新闻'
            data = json.loads(response.body.decode('utf-8').replace('var newsJason = ', '').replace('category',
                                                                                                    '\"category\"').replace(
                'item', '\"item\"'))
            category = data['category']
            item = data['item']
            for i in item:
                meta['title'] = i[1].strip()
                meta['third_tag'] = category[i[0]][0]
                url = i[2]
                yield scrapy.Request(url=url, callback=self.get_content, meta=meta)
        # elif meta['first_tag'] == '房产百科':
        #     urls = response.xpath('//*[@class="article"]')
        #     for i in urls:
        #         meta['title'] = i.xpath('*[@class="article-title"]/a/text()').extract_first().strip()
        #         url = i.xpath('*[@class="article-title"]/a/@href').extract_first()
        #         yield scrapy.Request(url=url,callback=self.get_content,meta=meta)
        else:
            data = json.loads(response.body.decode('utf-8'))
            if data != []:
                for i in data:
                    meta['title'] = i['title'].strip()
                    url = 'http://www.sohu.com/a/{}_{}'.format(i['id'], i['authorId'])
                    yield scrapy.Request(url=url, callback=self.get_content, meta=meta)
                currentPage = int(re.search(r'page=(\d+)', response.url).group(1))
                nextJson = re.sub(r'page=\d+', 'page=' + str(currentPage + 1), response.url)
                yield scrapy.Request(url=nextJson, callback=self.get_urls, meta=meta)

    def get_content(self, response):
        # print(response.body.decode('utf-8'))
        meta = response.meta
        item = JoviLonglasttimeItem()
        if meta['first_tag'] == '房产百科':
            contents = response.xpath('//*[@class="substance"]//text()').extract()
            try:
                source = response.xpath('//*[contains(@id,"source-address")]//text()').extract_first().strip()
            except:
                source = ''
            label = []
        else:
            contents = response.xpath(
                '//*[@class="article"]/p[not(@data-role)]//text()|//*[@class="article-text"]/p//text()').extract()
            label = response.xpath('//*[@class="tag"]/a//text()').extract()

            try:
                source = response.xpath('//*[@class="user-info"]/h4/a/text()').extract_first().strip()
            except:
                source = ''
        item['update_time'] = ''
        article_content = ''
        pattern = r'返回搜狐|原标题：|选自：|公众号|▲|文章来自|本文|来源|｜|来自网络|作者：|声明：|译自|如有侵权|\||编辑：|编者按|往期回顾|记者|点击进入|联合出品|【精彩推荐】|·|导读'
        for i in contents:
            if re.search(pattern, i):
                continue
            else:
                article_content += i.strip()
        item['article_content'] = article_content.replace('\r', '').replace('\n', '').replace('\t', '').replace(
            '\u3000', '').replace('\xa0', '')
        item['label'] = label
        item['source'] = source
        item['article_url'] = response.url
        item['article_title'] = meta['title']
        item['first_tag'] = meta['first_tag']
        item['second_tag'] = meta['second_tag']
        item['third_tag'] = meta['third_tag']
        yield item
