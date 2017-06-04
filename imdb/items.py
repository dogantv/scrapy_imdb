# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    title = scrapy.Field()
    content_type = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    duration = scrapy.Field()
    date_published = scrapy.Field()
    rating = scrapy.Field()
    vote_count = scrapy.Field()
    directors = scrapy.Field()
    writers = scrapy.Field()
    cast = scrapy.Field()
    color = scrapy.Field()
    genres = scrapy.Field()
    country = scrapy.Field()
    language = scrapy.Field()
    keywords = scrapy.Field()
    locations = scrapy.Field()
    modified_date = scrapy.Field()

