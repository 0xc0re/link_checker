link_checker
============

Python (scrapy) web crawler that records offsite links and image sources.

Uses a customized OffsiteMiddleware that allows one follow to an offsite
source, but will not follow *from* an offsite source.

To dump these "broken" links to a csv file:

$ scrapy crawl link_checker -o crawl.csv
