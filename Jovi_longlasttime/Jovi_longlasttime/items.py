# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JoviLonglasttimeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    first_tag = scrapy.Field()
    second_tag = scrapy.Field()
    third_tag = scrapy.Field()
    article_url = scrapy.Field()
    article_title = scrapy.Field()
    article_content = scrapy.Field()
    update_time = scrapy.Field()
    source = scrapy.Field()
    label = scrapy.Field()


class BlogItem(scrapy.Item):
    name = scrapy.Field()
    fans = scrapy.Field()
    guanzhu = scrapy.Field()
    articles = scrapy.Field()
    first_tag = scrapy.Field()
    second_tag = scrapy.Field()
    intro = scrapy.Field()
    address = scrapy.Field()
