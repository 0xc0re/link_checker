# -*- coding: utf-8 -*-

from six.moves.urllib.parse import urlparse, urljoin
import httplib
import re
import sys
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.http import HtmlResponse
import scrapy.utils.response
from link_checker.items import LinkItem
from scrapy import log, Selector

class LCheckSpider(CrawlSpider):
    name = 'lcheck'
    allowed_domains = [
        'edlinesites.net',
        'kentfieldschools.org',
        'sites.google.com'
    ]
    valid_domains = [
        'edlinesites.net',
        'kentweb.kentfieldschools.org',
        'sites.google.com'
    ]
    follow_domains = [
        'edlinesites.net'
    ]
    test_re = r'^(.*\.)?(%s)$' % '|'.join(re.escape(d) for d in follow_domains)
    test_ed = re.compile(test_re)
    valid_re = r'^(.*\.)?(%s)$' % '|'.join(re.escape(d) for d in valid_domains)
    valid_ed = re.compile(valid_re)
    html_ed = re.compile(r'\/html')
    start_urls = (
        'http://www.edlinesites.net/pages/Kentfield_School_District/Board_of_Trustees/Board_Members/Ashley_Paff',
        'http://www.edlinesites.net/pages/Kentfield_School_District',
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
    
    def domain_match(self, urlobj, regex):
        host = urlobj.hostname
        return host and bool(regex.search(host))
        
    def get_base_url(self, response):
        try:
            return scrapy.utils.response.get_base_url(response)
        except:
            pass
        return ''
        
    def abs_url(self, base_url, rel_url):
        url = rel_url
        if base_url != '' and urlparse(rel_url).scheme == '':
            url = urljoin(base_url, url)
        return url.replace('/../', '')

    def check_page(self, response, is_start):
        abs_link_url   = response.url
        urlobj = urlparse(abs_link_url)
        valid_domain   = self.domain_match(urlobj, self.valid_ed)
        if not is_start and not valid_domain and not isinstance(response, HtmlResponse):
            # offsite link
            item = LinkItem()
            item['link_type']    = 'link'
            item['page_url']     = response.request.headers.get('Referer', None)
            item['rel_link_url'] = abs_link_url
            item['abs_link_url'] = abs_link_url
            item['file_urls']    = [abs_link_url]
            item['valid']        = False
            item['ok']           = True
            yield item
                
        # images on valid pages        
        if valid_domain:
            hxs = Selector(response)
            image_urls = hxs.xpath('//img/@src').extract()
            base_url = self.get_base_url(response)
            for image_url in image_urls:
                abs_link_url   = self.abs_url(base_url, image_url)
                urlobj = urlparse(abs_link_url)
                if urlobj.scheme == 'http' or urlobj.scheme == 'https':
                    valid_domain   = self.domain_match(urlobj, self.valid_ed)
                    valid_response = (self.get_status_code(abs_link_url) < 400)
                    if not (valid_domain and valid_response):
                        item = LinkItem()
                        item['link_type']    = 'image'
                        item['page_url']     = response.url
                        item['rel_link_url'] = image_url
                        item['abs_link_url'] = abs_link_url
                        item['file_urls']    = [abs_link_url]
                        item['valid']        = valid_domain
                        item['ok']           = valid_response
                        yield item
        
    def parse_start_url(self, response):
        return self.check_page(response, True)
        # return super(CheckerSpider, self).parse_start_url(response)

    def parse_link(self, response):
        log.msg('parse_link %s' % response.url, level=log.DEBUG)
        return self.check_page(response, False)
        