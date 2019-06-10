# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html


import base64
import random
import time

import redis
from scrapy import signals
from scrapy.exceptions import IgnoreRequest
# from selenium.webdriver.common.keys import Keys
from scrapy.http import HtmlResponse
from selenium import webdriver

from Jovi_longlasttime.Use_agent import UA_LIST
from .proxy_pool import proxy_pool
from .tools.bloomfilter import BloomFilter

class BloomFilterMiddleware(object):
    def __init__(self,host,port,db,capacity,error_rate):
        self.redis = redis.StrictRedis(host,port,db)
        self.bloomfilter = BloomFilter(redis=self.redis,capacity=capacity,error_rate=error_rate,redis_key='JOVI_URLS')

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            host=crawler.settings.get('REDIS_HOST'),
            port=crawler.settings.get('REDIS_PORT'),
            db=crawler.settings.get('REDIS_DB'),
            capacity = crawler.settings.get('BLOOM_CAPACITY'),
            error_rate = crawler.settings.get('BLOOM_ERROR_RATE')
        )

    def process_request(self,request,spider):
        if self.bloomfilter.contains(request.url):
            raise IgnoreRequest('已经爬过此url----%s'%request.url)
        return None



class JoViLongLastTimeSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class JoViLongLastTimeDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ProxyMiddleware(object):

    def __init__(self):
        # self.random_proxy = random.choice(proxy_pool).replace('turing:025851@', '')
        self.proxy_user_pass = "turing:025851"
        self.proxyUser = 'turing'
        self.proxyPass = '025851'
        self.proxyAuth = "Basic " + base64.urlsafe_b64encode(
            bytes((self.proxyUser + ":" + self.proxyPass), "ascii")).decode("utf8")

    def process_request(self, request, spider):
        request.meta['proxy'] = random.choice(proxy_pool).replace('turing:025851@', '')
        request.headers['Proxy-Authorization'] = self.proxyAuth
        return None


class UaMiddleware(object):
    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(UA_LIST)
        return None


class SeleniumMiddleware(object):
    def __init__(self, codes):
        # 设置图片不加载
        # codes = 'window.scrollTo(1,document.body.scrollHeight)'
        chrome_opt = webdriver.ChromeOptions()
        prefs = {'profile.managed_default_content_settings.images': 2}
        chrome_opt.add_experimental_option('prefs', prefs)
        # chrome_opt.add_argument('--headless')
        self.browser = webdriver.Chrome(executable_path='D:\浏览器驱动\chromedriver.exe', chrome_options=chrome_opt)
        self.codes = codes
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            codes=crawler.settings.get('CODES')
        )

    def close_spider(self, spider):
        self.browser.close()

    def process_request(self, request, spider):
        if '/channel/' in request.url:
            self.browser.get(request.url)
            time.sleep(5)
            script = self.codes
            page = 1
            # tiaojian =  not('暂无更多新闻' in self.browser.page_source) and not('该频道暂无新闻，看看其他频道吧~' in self.browser.page_source) and page<200 and n
            while not ('暂无更多新闻' in self.browser.page_source) and not (
                    '该频道暂无新闻，看看其他频道吧~' in self.browser.page_source) and page < 100:
                self.browser.execute_script(script)
                time.sleep(1)
                page += 1
            return HtmlResponse(url=request.url, body=self.browser.page_source, request=request, encoding='utf-8',
                                status=200)
        else:
            return None
        # ignored_exceptions参数可以为下面的  配合使用
        # #until(method, message='')
        #     调用该方法体提供的回调函数作为一个参数，直到返回值为True
        # until_not(method, message='')
        #     调用该方法体提供的回调函数作为一个参数，直到返回值为False


class redisMiddleware(object):
    def __init__(self, redis_host, redis_port, redis_db):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.r = redis.Redis(host=self.redis_host, port=self.redis_port, db=self.redis_db)

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(redis_host=crawler.settings.get('REDIS_HOST'),
                redis_port=crawler.settings.get('REDIS_PORT'),
                redis_db=crawler.settings.get('REDIS_DB'),
                )
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        name = spider.__class__.__name__
        if self.r.sismember(name, request.url):
            # print('url已经存在')
            raise IgnoreRequest("IgnoreRequest : %s" % request.url)
        else:
            return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RefererMiddleware(object):
    def process_request(self, request, spider):
        request.headers['Referer'] = 'https://mini.eastday.com'
        return None


