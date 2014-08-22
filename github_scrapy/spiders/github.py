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
    start_urls = ["https://github.com/angular/angular.js/network/members"]
    crawledLinks = []
    out_links = []

    def parse(self, response):
        selector = HtmlXPathSelector(response)
        pageurls = selector.xpath('//div[@class="repo"]/a[1]/@href').extract()
        for url in pageurls:           
            url = 'https://github.com' + url + '?tab=repositories'
            if not url in self.crawledLinks:
                self.crawledLinks.append(url)
                yield Request(url, callback = self.parse_user)



    def parse_user(self, response):        
        regex_selector = re.compile('language">(.*?)</li>[^\b]+?class="repolist-name">[^\b]+?<a\s+href="(.*?)".*?>(.*?)</a>', re.MULTILINE)
        matches = regex_selector.findall(response.body)

        if matches:
            for item in matches:     
                sublink = item[1]
                if not sublink in self.out_links:
                    self.out_links.append(sublink)
                    text2 = "%s,https://github.com%s,%s" % (item[0], item[1], item[2])
                    text = "<tr><td>%s</td><td><a href=\"https://github.com%s\">%s</a></td></tr>" % (item[0], item[1], item[2])
                    self.csv_writer_.write('%s\n' % text2)
                    self.f_writer_.write('%s\n' % text)   
                    

        

    def __init__(self):
        html_filename = "test.html"
        csv_filename = "test.csv"

        result = re.search(r'https:\/\/.*?\/.*?\/(.*?)\/', self.start_urls[0], re.IGNORECASE) 
        if result:
            #print "-----------------------%s" % result.group(1)
            html_filename = "%s.html" % result.group(1)
            csv_filename = "%s.csv" % result.group(1)

        self.f_writer_ = open(html_filename,'w')
        self.f_writer_.write('<html><body><table>')
        self.csv_writer_ = open(csv_filename, 'w')

    def __del__(self):
        self.csv_writer_.close()

        self.f_writer_.write('</table></body></html>')
        self.f_writer_.close()