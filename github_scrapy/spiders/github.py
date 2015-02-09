#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys
reload(sys)
sys.setdefaultencoding('gb18030') 
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
    start_urls = ["https://github.com/JakeWharton/ActionBarSherlock/network/members"]
    crawledLinks = []
    out_links = []

    def parse(self, response):
        selector = HtmlXPathSelector(response)
        pageurls = selector.xpath('//div[@class="repo"]/a[1]/@href').extract()
        for url in pageurls:           
            url = 'https://github.com' + url + '/repositories'
            if not url in self.crawledLinks:
                self.crawledLinks.append(url)
                self.log_.write('%s\n' % url)
                yield Request(url, callback = self.parse_user)



    def parse_user(self, response):        
        regex_selector = re.compile('repo-list-stats">([^\b]+?)<a[^\b]+?git-branch"[^\b]+?</span>([^\b]+?)</a>[^\b]+?repo-list-name">[^\b]+?<a\shref="(.*?)">([^\b]+?)</a>', re.MULTILINE)
        matches = regex_selector.findall(response.body)

        if matches:
            for item in matches:     
                sublink = item[2]
                if not sublink in self.out_links:
                    self.out_links.append(sublink)
                    text2 = "%s,https://github.com%s,%s,%s" % (item[0].strip(), item[2].strip(), item[3].strip(), item[1].strip().replace(',', ''))
                    text = "<tr><td>%s</td><td><a href=\"https://github.com%s\">%s</a></td><td>%s</td></tr>" % (item[0].strip(), item[2].strip(), item[3].strip(), item[1].strip())
                    self.csv_writer_.write('%s\n' % text2)
                    self.f_writer_.write('%s\n' % text)   

        page_selector = HtmlXPathSelector(response)
        url_list = page_selector.xpath('//div[@class="pagination"]/a/@href').extract()
        for url in url_list:
            url = 'https://github.com' + url
            if not url in self.crawledLinks:
                self.crawledLinks.append(url)
                self.log_.write('%s\n' % url)
                yield Request(url, callback = self.parse_user)
                #print url
                #os.system("pause")    

        
        #name_list = selector.xpath('//h3[@class="repolist-name"]/a/text()').extract()
        #url_list = selector.xpath('//h3[@class="repolist-name"]/a/@href').extract()        
        #print name, suburl

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
        self.log_ = open("log.txt", 'w')

    def __del__(self):
        self.log_.close()
        self.csv_writer_.close()

        self.f_writer_.write('</table></body></html>')
        self.f_writer_.close()