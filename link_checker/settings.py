# -*- coding: utf-8 -*-

# Scrapy settings for link_checker project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'link_checker'

SPIDER_MODULES = ['link_checker.spiders']

NEWSPIDER_MODULE = 'link_checker.spiders'

ITEM_PIPELINES = {
    'link_checker.pipelines.InvalidLinkPipeline': 300
}

# We use custom offsite middleware so we can track certain offsite links
SPIDER_MIDDLEWARES = {
    'link_checker.middleware.OffsiteRefererMiddleware': 300,
    'scrapy.contrib.spidermiddleware.offsite.OffsiteMiddleware': None
}

LOG_FILE  = 'link_checker.log'
LOG_LEVEL = 'INFO'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'link_checker (+http://www.kentfieldschools.org)'
