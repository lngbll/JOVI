import codecs
import json
import random
import re
import time

import requests
from lxml import etree

headers1 = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': 'SINAGLOBAL=3265554702852.2134.1540779784224; login_sid_t=0697083a3b69b58897a4414937f3d4f4; cross_origin_proto=SSL; _s_tentry=www.google.com.hk; Apache=5008793828465.738.1540948385179; ULV=1540948385184:5:5:5:5008793828465.738.1540948385179:1540894202202; YF-Page-G0=140ad66ad7317901fc818d7fd7743564; wb_view_log_5234071528=1920*10801; TC-Page-G0=8dc78264df14e433a87ecb460ff08bfe; crossidccode=CODE-gz-1GhG3L-27QukX-tO6pSQMtAv9ItC1528bc5; appkey=; UOR=www.google.com.hk,www.weibo.com,login.sina.com.cn; SUHB=0rrLlFGBxYCsch; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WhTFGMYuXqMc8ZBnmZuAPaL5JpV2K27SoeNSK5RSKi5MP2Vqcv_; SUB=_2AkMshZ1bdcPxrAZTm_wVy2rnboVH-jyfUPStAn7uJhMyAxgv7ksuqSVutBF-XE_eQDhy4xpNxXGbFAZWo_puubSw',
    'Pragma': 'no-cache',
    'Host': 'd.weibo.com',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'https://d.weibo.com/1087030002_417',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'
}
headers2 = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': 'YF-Page-G0=04608cddd2bbca9a376ef2efa085a43b; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WhUBpU0NCwhlqqs9ZIqqKd5; _s_tentry=passport.weibo.com; Apache=3369042096576.6377.1540952848290; SINAGLOBAL=3369042096576.6377.1540952848290; ULV=1540952848300:1:1:1:3369042096576.6377.1540952848290:; SUB=_2AkMshZDOf8NxqwJRmP4VzW3kaox1zArEieKa2WEVJRMxHRl-yj9jqmVftRB6BwW-IZ53wD1qWHJ9IeembGMTLBt0OmHt; TC-Page-G0=fd45e036f9ddd1e4f41a892898506007',
    'Host': 'd.weibo.com',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',

}
headers3 = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': 'YF-Page-G0=04608cddd2bbca9a376ef2efa085a43b; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WhUBpU0NCwhlqqs9ZIqqKd5; _s_tentry=passport.weibo.com; Apache=3369042096576.6377.1540952848290; SINAGLOBAL=3369042096576.6377.1540952848290; ULV=1540952848300:1:1:1:3369042096576.6377.1540952848290:; SUB=_2AkMshZDOf8NxqwJRmP4VzW3kaox1zArEieKa2WEVJRMxHRl-yj9jqmVftRB6BwW-IZ53wD1qWHJ9IeembGMTLBt0OmHt; TC-Page-G0=fd45e036f9ddd1e4f41a892898506007',
    'Host': 'd.weibo.com',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',

}


def get_content(url):
    response = requests.get(url='https://d.weibo.com' + url, headers=headers3)
    pattern = r'FM\.view\((.*?)\)</script>'
    datas = re.findall(pattern, response.text)
    names = []
    for data in datas:
        if 'follow_list' in data:
            data = json.loads(data)
            title = etree.HTML(data['html']).xpath('//ul[@class="follow_list"]/li//a[@class="S_txt1"]/@title')
            for i in title:
                names.append(i)
            return names


def get_first_tags(url):
    response = requests.get(url=url, headers=headers1)
    pattern = r'<script>FM\.view\((.*?)\)</script>'
    data = re.findall(pattern, response.text)
    for index in range(len(data)):
        if '媒体精英' in data[index]:
            # print(index)
            data = json.loads(data[index])
            html = codecs.escape_decode(bytes(data['html'], encoding='utf-8'))[0].decode('utf-8')
            names = etree.HTML(html).xpath('//ul[@class="ul_item clearfix"]/li[position()>5]/a/span[2]/text()')
            hrefs = etree.HTML(html).xpath('//ul[@class="ul_item clearfix"]/li[position()>5]/a/@href')
            print(names)
            # print(hrefs)
            return dict(zip(names, hrefs))


def get_second_tags(url):
    response = requests.get(url=url, headers=headers2)
    # print(response.text)
    # print(response.url,response.text)
    pattern = r'FM\.view\((.*?)\)</script>'
    datas = re.findall(pattern, response.text)
    for data in datas:
        if 'list_box S_bg1 S_line1' in data:
            data = json.loads(data)
            html = codecs.escape_decode(bytes(data['html'], encoding='utf-8'))[0].decode('utf-8')
            names = etree.HTML(html).xpath('//ul[@class="ul_text clearfix"]/li/a/text()')
            # print(names)
            if len(names) > 1:
                names = etree.HTML(html).xpath('//div[@class="list_box S_bg1 S_line1"]/ul/li[position()>1]/a/text()')
                hrefs = etree.HTML(html).xpath('//div[@class="list_box S_bg1 S_line1"]/ul/li[position()>1]/a/@href')

            else:
                names = etree.HTML(html).xpath('//div[@class="list_box S_bg1 S_line1"]/ul/li/a/text()')
                hrefs = etree.HTML(html).xpath('//div[@class="list_box S_bg1 S_line1"]/ul/li/a/@href')

            return dict(zip(names, hrefs))


def get_pages(url):
    response = requests.get(url=url, headers=headers3)
    print(response.url)
    # print(response.text)
    # print(response.text)
    pattern = r'FM\.view\((.*?)\)</script>'
    datas = re.findall(pattern, response.text)
    pages = []
    for data in datas:
        if '下一页' in data:
            data = json.loads(data)
            html = codecs.escape_decode(bytes(data['html'], encoding='utf-8'))[0].decode('utf-8')
            max_page = etree.HTML(html).xpath('//div[@class="W_pages"]/a/@href')
            # print(max_page[-2])
            num = int(re.search(r'page=(\d+)', max_page[-2]).group(1))
            for i in range(1, num + 1):
                page = re.sub(r'page=\d+', 'page=' + str(i), max_page[-2])
                pages.append(page)
    if len(pages) == 0:
        one_page = response.url.replace('https://d.weibo.com', '')
        pages.append(one_page)
    page_num = len(pages)
    print('共%s页' % page_num)
    return pages


#
# def get_html(response,index,pattern):
#     data = re.findall(pattern, response.text)
#     print(len(data))
#     data = json.loads(data[index])
#     html = codecs.escape_decode(bytes(data['html'], encoding='utf-8'))[0].decode('utf-8')
#     return html


def main():
    url = 'https://d.weibo.com/1087030002_417'
    channel1 = get_first_tags(url)
    with open('e:\\微博博主列表字典.txt', 'a', encoding='utf-8') as file:
        for k, v in channel1.items():
            if k != '更多':
                _v = 'https:' + v
                channel2 = get_second_tags(_v)
                for m, n in channel2.items():
                    print('开始下载%s\\%s' % (k.strip(), m.strip()))
                    _n = 'https:' + n
                    # print(_n)
                    pages = get_pages(_n)
                    # with Pool(6) as pool:
                    #     # 多线程调用函数，得到最终结果
                    contents = []
                    for page in pages:
                        try:
                            time.sleep(random.random() * 2)
                            content = get_content(page)
                            print(content)
                            contents += content
                        except:
                            print('页面抓取异常  %s' % page)
                    print('下载完成！开始写入文件')
                    for j in contents:
                        content = '%s %s %s\n' % (j, k.strip(), m.strip())
                        file.write(content)
                    print("数据写入完成")


if __name__ == '__main__':
    main()
