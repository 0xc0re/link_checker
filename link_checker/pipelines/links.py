# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
from six.moves.urllib.parse import urlparse
from scrapy.exceptions import DropItem

class InvalidLinksPipeline(object):
    def process_item(self, item, spider):
        if item['valid'] and item['ok']:
            raise DropItem('Link ok: %s' % item['abs_link_url'])
        else:
            return item
