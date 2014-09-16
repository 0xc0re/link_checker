# -*- coding: utf-8 -*-

from six.moves.urllib.parse import urlparse, urljoin
import httplib
import re
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.response import get_base_url
from link_checker.items import LinkItem
from scrapy import log, Selector

class LCheckSpider(CrawlSpider):
    name = 'lcheck'
    test_ed = re.compile(r'^(.*\.)?(%s)$' % re.escape('edlinesites.net'))
    allowed_domains = [
        'edlinesites.net',
        'kentfieldschools.org',
        'sites.google.com'
    ]
    follow_domains = [
        'edlinesites.net'
    ]
    start_urls = (
        'http://www.edlinesites.net/pages/Kentfield_School_District',
    #    'http://www.edlinesites.net/pages/Bacich_Elementary_School',
    #    'http://www.edlinesites.net/pages/Kent_Middle_School',
    )
    # Add our callback which will be called for every found link
    rules = (
            Rule(LinkExtractor(), follow=True, callback='parse_link'),
    )
    log.start()

    def get_status_code(self, url):
        """ This function retreives the status code of a website by requesting
            HEAD data from the host. This means that it only requests the headers.
            If the host cannot be reached or something else goes wrong, it returns
            500 instead.
        """
        try:
            o = urlparse(url)
            host = o.hostname
            if not host:
                return 500
            conn = httplib.HTTPConnection(o.hostname)
            conn.request("HEAD", o.path)
            status = int(conn.getresponse().status)
            return status
        except StandardError as e:
            return 500
    
    def domain_match(self, url, regex):
        o = urlparse(url)
        host = o.hostname
        return host and bool(regex.search(host))

    def check_page(self, response, is_start):
        page_url = None
        if is_start:
            page_url = response.url
        else:
            page_url = response.request.headers.get('Referer', None)
            
        # try to stop following if we are on a "foreign" page
        if not self.domain_match(page_url, self.test_ed):
            log.msg('Returning without yield for %s' % page_url, level=log.DEBUG)
            return
        else:
            if not is_start:
                item = LinkItem()
                item['ltype']    = 'link'
                item['page_url'] = page_url
                item['link_url'] = response.url
                item['valid']    = self.domain_match(response.url, self.test_ed)
                item['ok']       = (response.status < 400)
                yield item
            base_url = get_base_url(response)
            hxs = Selector(response)
            image_urls = hxs.xpath('//img/@src').extract()
            for image_url in image_urls:
                abs_image_url = urljoin(base_url, image_url)
                item = LinkItem()
                item['ltype']    = 'image'
                item['page_url'] = page_url
                item['link_url'] = image_url
                item['valid']    = self.domain_match(abs_image_url, self.test_ed)
                item['ok']       = (self.get_status_code(abs_image_url) < 400)
                yield item
        
    def parse_start_url(self, response):
        return self.check_page(response, True)
        # return super(CheckerSpider, self).parse_start_url(response)

    def parse_link(self, response):
        log.msg('parse_link %s' % response.url, level=log.DEBUG)
        return self.check_page(response, False)
        