# -*- coding: utf-8 -*-

import os
from hashlib import sha224

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import redis
from scrapy.exceptions import DropItem


class Duppipline(object):
    def process_item(self, item, spider):
        if item['article_title']:
            if len(item['article_content']) < 200:
                print('文章短----%s----%s' % (item['article_title'], item['article_url']))
                raise DropItem
            else:
                return item
        else:
            print('没有标题----%s' % item['article_url'])
            raise DropItem


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
        s1 = sha224(item['article_title'].encode('utf-8'))
        fp = s1.hexdigest()
        if self.r.sismember('article_title_fp_new', fp):
            print('文章重复----%s-----%s' % (item['article_title'], item['article_url']))
            raise DropItem
        else:
            self.r.sadd('article_title_fp_new', fp)
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


# 对于有三级标签的spider,使用这个pipeline
class To_csv(object):
    def __init__(self, START_DIR, stats):

        self.stats = stats
        self.START_DIR = START_DIR
        self.stats.set_value('*总数', 0)
        if os.path.exists(self.START_DIR):
            os.chdir(self.START_DIR)
        else:
            os.mkdir(self.START_DIR)
            os.chdir(self.START_DIR)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            START_DIR=crawler.settings.get('START_DIR'),
            stats=crawler.stats
        )

    def process_item(self, item, spider):
        first_tag = item['first_tag']
        second_tag = item['second_tag']
        third_tag = item['third_tag']
        if os.path.exists('%s\%s' % (self.START_DIR, first_tag)):
            os.chdir('%s\%s' % (self.START_DIR, first_tag))
        else:
            os.mkdir('%s\%s' % (self.START_DIR, first_tag))
            self.stats.set_value('*' + first_tag, 0)
            os.chdir('%s\%s' % (self.START_DIR, first_tag))
        if os.path.exists('%s' % second_tag):
            os.chdir('.\%s' % second_tag)
        else:
            os.mkdir('%s' % second_tag)
            self.stats.set_value('*' + first_tag + '_' + second_tag, 0)
            os.chdir('.\%s' % second_tag)
        with open(third_tag + ".txt", 'a', encoding='utf-8') as file:
            file.write((item['article_title'] + "," + item['article_content'] + '\n'))
            print(item['article_title'] + "," + item['article_content'] + '\n')
            # print('成功保存----%s' % self.stats.get_value('item_scraped_count'))
        self.stats.inc_value('*' + first_tag)
        self.stats.inc_value('*' + first_tag + '_' + second_tag)
        self.stats.inc_value('*总数')
        return item

    # def close_spider(self, spider): #统计函数
    #     os.chdir('e:\\统计')
    #     name = spider.__class__.__name__
    #     a = self.stats.get_stats()
    #     date = self.stats.get_value('start_time').strftime('%m%d')
    #     self.stats.set_value('start_time', 0)
    #     self.stats.set_value('finish_time', 0)
    #     with open('e:\\统计\\%s%s.txt' % (name, date), 'w', encoding='utf-8') as f:
    #         for i in a.keys():
    #             if i.startswith('*'):
    #                 lines = '%s:%d\n' % (i, a[i])
    #                 f.write(lines)




# 对于只有二级标签的spider,使用这个pipeline
class To_csv1(object):
    def __init__(self, stats, START_DIR):
        self.stats = stats
        self.START_DIR = START_DIR
        self.stats.set_value('*总数',0)
        if os.path.exists(self.START_DIR):
            os.chdir(self.START_DIR)
        else:
            os.mkdir(self.START_DIR)
            os.chdir(self.START_DIR)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            START_DIR=crawler.settings.get('START_DIR'),
            stats = crawler.stats
        )

    def process_item(self, item, spider):
        first_tag = item['first_tag']
        second_tag = item['second_tag']
        if os.path.exists('%s\%s' % (self.START_DIR, first_tag)):
            os.chdir('%s\%s' % (self.START_DIR, first_tag))
        else:
            self.stats.set_value('*'+second_tag,0)
            os.mkdir('%s\%s' % (self.START_DIR, first_tag))
            os.chdir('%s\%s' % (self.START_DIR, first_tag))
        with open(second_tag + ".txt", 'a', encoding='utf-8') as file:
            file.write((item['article_title'] + "," + item['article_content'] + '\n'))
            print('成功保存----%d' % self.stats.get_value('*总数'))
            self.stats.inc_value('*'+second_tag)
            self.stats.inc_value('*总数')
        return item

    def close_spider(self,spider):
        # os.chdir('e:\\统计')
        # name = spider.__class__.__name__
        # a = self.stats.get_stats()
        # date = self.stats.get_value('start_time').strftime('%m%d')
        # self.stats.set_value('start_time', 0)
        # self.stats.set_value('finish_time', 0)
        # with open('e:\\统计\\%s%s.txt' % (name, date), 'w', encoding='utf-8') as f:
        #     record = list()
        #     for k,v in a.items():
        #         if k.startswith('*'):
        #             record.append('%s:%s'%(k,v))
        #     record.sort()
        #     f.write(str(record))
        os.chdir('e:\\统计')
        name = spider.__class__.__name__
        a = self.stats.get_stats()
        date = self.stats.get_value('start_time').strftime('%m%d')
        self.stats.set_value('start_time', 0)
        self.stats.set_value('finish_time', 0)
        with open('e:\\统计\\%s%s.txt' % (name, date), 'w', encoding='utf-8') as f:
            for i in a.keys():
                if i.startswith('*'):
                    lines = '%s:%d\n' % (i, a[i])
                    f.write(lines)
