# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item 

def downloaded_file_path(value):
    return value[0]['path']

def empty_string(value):
    return ''
    
class LinkItem(Item):
    # define the fields for your item here like:
    link_type    = Field()
    page_url     = Field()
    rel_link_url = Field()
    abs_link_url = Field()
    valid        = Field()
    ok           = Field()
    # Required for FilesPipeline
    file_urls    = Field(serializer=empty_string)
    files        = Field(serializer=downloaded_file_path)