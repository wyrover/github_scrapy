#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys
from scrapy.spider import Spider
from scrapy.utils.url import urljoin_rfc
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
import urllib2
import urllib
import re
import json

class GithubSpider(Spider):
    name = "github"
    allowed_domains = ["github.com"]
    start_urls = ["https://github.com/jakubroztocil/httpie/network/members"]

    def parse(self, response):
        selector = HtmlXPathSelector(response)
        pageurls = selector.xpath('//div[@class="repo"]/a[1]/@href').extract()
        for url in pageurls:           
            url = 'https://github.com' + url + '?tab=repositories'
            yield Request(url, callback = self.parse_user)



    def parse_user(self, response):        
        regex_selector = re.compile('language">(.*?)</li>[^\b]+?class="repolist-name">[^\b]+?<a\s+href="(.*?)">(.*?)</a>', re.MULTILINE)
        matches = regex_selector.findall(response.body)

        if matches:
            for item in matches:                       
                text = "<tr><td>%s</td><td><a href=\"https://github.com%s\">%s</a></td></tr>" % (item[0], item[1], item[2])
                self.f_writer_.write('%s\n' % text)   
                self.csv_writer_.write('%s,https://github.com%s,%s\n' % (item[0], item[1], item[2]))

        #name_list = selector.xpath('//h3[@class="repolist-name"]/a/text()').extract()
        #url_list = selector.xpath('//h3[@class="repolist-name"]/a/@href').extract()        
        #print name, suburl

    def __init__(self):
        self.f_writer_ = open('github.html','w')
        self.f_writer_.write('<html><body><table>')
        self.csv_writer_ = open('github.csv', 'w')

    def __del__(self):
        self.csv_writer_.close()

        self.f_writer_.write('</table></body></html>')
        self.f_writer_.close()