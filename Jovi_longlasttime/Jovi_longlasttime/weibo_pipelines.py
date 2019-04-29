# -*- coding: utf-8 -*-

import os
from hashlib import sha1

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import redis
from scrapy.exceptions import DropItem


class Duppipline(object):
    def process_item(self, item, spider):
        if item['article_title'] == None:
            raise DropItem('没有抓到标题：《%s》(%s)' % (item['article_title'], item['article_url']))
        elif len(item['article_content']) < 200:
            raise DropItem('文章太短了：《%s》(%s)' % (item['article_title'], item['article_url']))
        else:
            return item


class Redispipline(object):
    def __init__(self, redis_host, redis_port, redis_db):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.r = redis.Redis(host=self.redis_host, port=self.redis_port, db=self.redis_db)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(redis_host=crawler.settings.get('REDIS_HOST'),
                   redis_port=crawler.settings.get('REDIS_PORT'),
                   redis_db=crawler.settings.get('REDIS_DB')
                   )

    def process_item(self, item, spider):
        name = spider.__class__.__name__
        # name='test'
        self.r.sadd(name, item['article_url'])
        # 生成fingerprint
        s1 = sha1(item['article_content'].encode('utf-8'))
        fp = s1.hexdigest()
        if self.r.sismember('article_title_fp1', fp):
            raise DropItem('重重重重重复复复复复了了了了了：《%s》（%s）' % (item['article_title'], item['article_url']))
        else:
            self.r.sadd('article_title_fp1', fp)
            return item


class Mongopipline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        collection_name = spider.__class__.__name__
        self.db[collection_name].insert_one(dict(item))

        # self.db['test'].update({'article_url': item['article_url']}, {'$set': dict(item)}, True)
        return item


class To_csv(object):
    def __init__(self, START_DIR):
        self.START_DIR = START_DIR
        if os.path.exists(self.START_DIR):
            os.chdir(self.START_DIR)
        else:
            os.mkdir(self.START_DIR)
            os.chdir(self.START_DIR)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            START_DIR=crawler.settings.get('START_DIR')
        )

    def process_item(self, item, spider):
        first_tag = item['first_tag']
        second_tag = item['second_tag']
        third_tag = item['third_tag']
        if os.path.exists('%s\%s' % (self.START_DIR, first_tag)):
            os.chdir('%s\%s' % (self.START_DIR, first_tag))
        else:
            os.mkdir('%s\%s' % (self.START_DIR, first_tag))
            os.chdir('%s\%s' % (self.START_DIR, first_tag))
        if os.path.exists('%s' % second_tag):
            os.chdir('.\%s' % second_tag)
        else:
            os.mkdir('%s' % second_tag)
            os.chdir('.\%s' % second_tag)
        with open(third_tag + ".txt", 'a', encoding='utf-8') as file:
            file.write((item['article_content'] + '\n'))
        return item
