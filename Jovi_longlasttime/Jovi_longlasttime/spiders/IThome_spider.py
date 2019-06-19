# -*- coding: utf-8 -*-
import re
import time

import scrapy

from Jovi_longlasttime.items import JoviLonglasttimeItem


class IthomeSpiderSpider(scrapy.Spider):
    name = 'IThome_spider'
    # allowed_domains = ['www.ithome.com']
    log_dir = 'e:\\日志文件夹\\JOVI新闻爬虫\\IT之家_spider'
    date = time.strftime('%Y-%m-%d', time.localtime())

    start_urls = ['https://www.ithome.com/sitemap/']

    custom_settings = {
        'LOG_FILE':'{}\\{}.log'.format(log_dir,date)
    }

    meta = {
        "first_tag": 'IT之家',
        'second_tag': '',
        'third_tag': '',
        'page': 1,
        'categoryid': '',
        # 'label':''
    }
    no_parse = ['iPad之家', 'Win7之家', 'Vista之家', '主题之家', 'Mac之家', 'VR之家', '软件之家', 'Win8.1之家', 'iPhone之家', 'IE之家',
                'Office之家', 'IT之外', 'WP之家', 'Mac之家', 'iOS之家']

    def parse(self, response):
        meta = self.meta
        nav = response.xpath('//div[@class="sitemap adblock"]/div[position()>1]')
        for i in nav:
            meta['second_tag'] = i.xpath('span/a/text()').extract_first().strip()
            if meta['second_tag'] not in self.no_parse:
                third_tag_nav = i.xpath('ul/li/a')
                for j in third_tag_nav:
                    meta['third_tag'] = j.xpath('text()').extract_first().strip()
                    # if meta['third_tag'] =='Win7快讯':
                    url = j.xpath('@href').extract_first()
                    yield scrapy.Request(url=url, callback=self.get_cateid, meta=meta)

    def get_cateid(self, response):
        meta = response.meta
        categoryid = re.search(r'categoryID =(\d+)', response.text, re.S).group(1)
        meta['categoryid'] = categoryid
        formData = {
            'categoryid': categoryid,
            'type': 'pccategorypage',
            'page': '1'
        }
        url = 'https://win7.ithome.com/ithome/getajaxdata.aspx'
        yield scrapy.FormRequest(url, formdata=formData, callback=self.get_url, meta=meta)

    def get_url(self, response):
        meta = response.meta
        if response.body != b'':
            urls = response.xpath('//li')
            for i in urls:
                url = i.xpath('a/@href').extract_first()
                # meta['label'] = i.xpath('//span[@class="tags"]/a/text()').extract()
                yield scrapy.Request(url=url, callback=self.get_content, meta=meta)
            meta['page'] += 1
            formData = {
                'categoryid': meta['categoryid'],
                'type': 'pccategorypage',
                'page': str(meta['page'])
            }
            if meta['page'] < 100:
                yield scrapy.FormRequest(response.url, callback=self.get_url, meta=meta, formdata=formData)
        else:
            print('%s共%d页抓取完成' % (meta['third_tag'], meta['page']))

    def get_content(self, response):
        meta = response.meta
        item = JoviLonglasttimeItem()
        # doc_info = json.loads(re.search(r'window\.yidian\.docinfo = (.*?)\n</script>',response.body.decode('utf-8'),re.S).group(1).replace('\\',''))
        artical_contents = response.xpath('//div[@class="post_content"]//p//text()').extract()
        content = ''
        pattern = r'相关阅读：|图文|说明：|原标题|原题|选自：|公众号|▲|文章来自|本文|来源|｜|来自网络|作者：|声明：|译自|如有侵权|\||编辑|编者|往期回顾|记者|点击进入|提示：|导语：|转载联系|责编'
        for i in artical_contents:
            if re.search(pattern, i, re.S):
                continue
            elif re.search(r'相关阅读：', i):
                break
            else:
                content += i.strip()
        item['article_content'] = content.replace('\r', '').replace('\t', '').replace('\n', '').replace('\xa0',
                                                                                                        '').replace(
            '\u3000', '')
        try:
            item['article_title'] = response.xpath('//div[@class="post_title"]//text()').extract_first().strip()
        except:
            item['article_title'] = ''
        item['first_tag'] = 'IT之家'
        item['second_tag'] = meta['second_tag']
        item['third_tag'] = meta['third_tag']
        item['article_url'] = response.url
        try:
            item['source'] = response.xpath('//span[@id="source_baidu"]/a/text()').extract_first()
        except:
            item['source'] = ''
        try:
            item['update_time'] = response.xpath('//span[@id="pubtime_baidu"]/text()').re_first('\d+-\d+-\d+')
        except:
            item['update_time'] = ''
        item['label'] = ''
        yield item
