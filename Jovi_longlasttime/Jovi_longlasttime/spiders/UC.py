# -*- coding: utf-8 -*-
import json
import re
import time
from datetime import datetime
import scrapy
from lxml import etree
from Jovi_longlasttime.items import JoviLonglasttimeItem


class UcSpider(scrapy.Spider):
    name = 'UC'
    # allowed_domains = ['zzd.sm.cn']
    start_urls = ['http://zzd.sm.cn/webapp/index?uc_param_str=dnnivebichfrmintcpgieiwidsudsv&zzd_from=zxzx']
    meta = {
        'title': '',
        'third_tag': '',
        'label': '',
        'source': '',

    }
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Cookie': 'sn=14960737088016682235; sm_diu=7cfa4c57ccdac9ec43cad92bace967ca%7C%7C11eef1244ad7bd31fb%7C1539746848',
        'Host': 'zzd.sm.cn',
        'Referer': 'http://zzd.sm.cn/webapp/index?uc_param_str=dnnivebichfrmintcpgieiwidsudsv&zzd_from=zxzx',
        'Pragma': 'no-cache',
    }
    no_parse = ['图片', '视频', '趣图', '摄影', '精品', '推荐']
    custom_settings = {
        'ITEM_PIPELINES':{
            'Jovi_longlasttime.pipelines.BloomFilterPipeline': 200,
            'Jovi_longlasttime.pipelines.Duppipline': 300,
            # # 'Jovi_longlasttime.pipelines.Mongopipline': 400,   #默认不开启MongoDB,节省内存资源
            'Jovi_longlasttime.pipelines.To_csv1': 500
        }
    }

    def parse(self, response):
        meta = self.meta
        channels = re.search(r' var channels = (.*?);', response.text, re.S).group(1)
        cate = json.loads(channels)
        for i in cate:
            name = i['name']
            meta['third_tag'] = name
            if name not in self.no_parse:
                # if name =='历史':

                id = i['id']
                meta['id'] = id
                meta['page'] = 1
                stamp = int(time.time() * 1000)
                url = 'http://zzd.sm.cn/iflow/api/v1/channel/{}?uc_param_str=dnnivebichfrmintcpgieiwidsudpf&zzd_from=zxzx&app=webapp&is_h5=1&client_os=webapp&sn=14960737088016682235&method=new&ftime=&count=20&summary=0&bid=800&m_ch=500&recoid=&_={}'.format(
                    id, stamp)
                productResponse = scrapy.Request(url=url, callback=self.get_url, meta=meta, headers=self.headers)
                productResponse.meta['dont_cache'] = True
                yield productResponse

    def get_url(self, response):
        meta = response.meta
        if meta['page'] < 200:
            res = json.loads(response.text)
            article = res['data']['articles']
            if article != {}:
                for i in article.keys():
                    is_ad = article[i]['op_mark']
                    if is_ad != '广告':
                        meta['title'] = article[i]['title']
                        meta['source'] = article[i]['source_name']
                        meta['label'] = article[i]['tags']
                        url = 'http://m.uczzd.cn/webview/news?aid=' + i
                        yield scrapy.Request(url=url, callback=self.get_content, meta=meta, dont_filter=False)
                next_key = list(article.keys())[-1]
                next_recoid = article[next_key]['recoid']
                channel_id = meta['id']
                time_stamp = int(time.time() * 1000)
                next_page = 'http://zzd.sm.cn/iflow/api/v1/channel/{}?uc_param_str=dnnivebichfrmintcpgieiwidsudpf&zzd_from=z' \
                            'xzx&app=webapp&is_h5=1&client_os=webapp&sn=14960737088016682235&method=his&' \
                            'count=20&summary=0&bid=800&m_ch=500&recoid={}&_=1539912277190'.format(channel_id,
                                                                                                   next_recoid,
                                                                                                   time_stamp)
                print('开始%s第%s页' % (meta['third_tag'], meta['page']))
                meta['page'] += 1
                yield scrapy.Request(url=next_page, callback=self.get_url, meta=meta, headers=self.headers)

    def get_content(self, response):
        try:
            meta = response.meta
            item = JoviLonglasttimeItem()
            content = re.search(r'"content":"(.*?)","thumbnails"', response.text, re.S).group(1)
            article_contents = etree.HTML(content).xpath('//p//text()')
            ptime = int(re.search(r'"publish_time":(\d+),', response.text, re.S).group(1))
            publish_time = datetime.fromtimestamp(int(ptime) / 1000)
            pub_time = str(publish_time).split(' ')[0]
            article_content = ''
            pattern = r'图文|说明：|原标题|原题|选自：|公众号|▲|文章来自|本文|来源|｜|来自网络|作者：|声明：|译自|如有侵权|\||编辑|编者|往期回顾|记者|点击进入|联合出品|提示：|导语：'
            for i in article_contents:
                if re.search(pattern, i, re.S):
                    continue
                else:
                    article_content += i.strip()
            item['article_content'] = article_content.replace('\r', '').replace('\n', '').replace('\t', '').replace('\xa0',
                                                                                                                    '').replace(
                '\u3000', '')
            item['first_tag'] = 'UC头条'
            item['second_tag'] = meta['third_tag']
            item['article_url'] = response.url
            item['source'] = meta['source']
            item['label'] = meta['label']
            item['update_time'] = pub_time
            item['article_title'] = meta['title']
            yield item
        except Exception:
            print('请求异常----%s' % response.url)
