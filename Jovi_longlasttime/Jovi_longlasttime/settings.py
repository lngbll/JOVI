# -*- coding: utf-8 -*-
import time

BOT_NAME = 'Jovi_longlasttime'

SPIDER_MODULES = ['Jovi_longlasttime.spiders']
NEWSPIDER_MODULE = 'Jovi_longlasttime.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'Jovi_longlasttime (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# DOWNLOAD_DELAY = 0.5    #东方头条都开始反爬了，只能龟速了，在限速的同时，每周爬虫改为并行处理
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# COOKIES_ENABLED = False


DOWNLOADER_MIDDLEWARES = {
    # 'Jovi_longlasttime.middlewares.ProxyMiddleware':300,
    'Jovi_longlasttime.middlewares.UaMiddleware': 400,
    # 'Jovi_longlasttime.middlewares.SeleniumMiddleware':500,
    'Jovi_longlasttime.middlewares.BloomFilterMiddleware': 200
}

ITEM_PIPELINES = {
        'Jovi_longlasttime.pipelines.BloomFilterPipeline': 200,
        'Jovi_longlasttime.pipelines.Duppipline': 100,
        # # 'Jovi_longlasttime.pipelines.Mongopipline': 400,   #默认不开启MongoDB,节省内存资源
        'Jovi_longlasttime.pipelines.To_csv': 500  # 三级文件夹
}

LOG_ENABLED = True
# LOG_FILE = None #日志文件有专门的日志文件夹，每个spider分别存储
LOG_LEVEL = 'INFO'
LOG_ENCODING = 'utf-8'
date = time.strftime('%Y-%m-%d', time.localtime())

MONGO_URI = 'localhost'
MONGO_DB = 'JOVI'

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 1

START_DIR = 'e:'
# DOWNLOAD_TIMEOUT=16
# COOKIES_ENABLED = False
# HTTPCACHE_ENABLED = T
CONCURRENT_REQUESTS_PER_DOMAIN = 200
CODES = 'window.scrollTo(1,document.body.scrollHeight)'
counter = dict()

# bloomfilter settings,一旦设置不可随便更改
BLOOM_CAPACITY = 100000000
BLOOM_ERROR_RATE = 0.00001
BLOOM_CAPACITY_URL = 1000000000
BLOOM_ERROR_RATE_URL = 0.00001

REDIRECT_ENABLED = True
