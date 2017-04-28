# -*- coding: utf-8 -*-
# 云南大理招投标网站
# 抓取不了
import scrapy
from scrapy import Request, FormRequest
from scrapy.selector import Selector

try:
    from scrapy.spiders import Spider
except:
    from scrapy.spiders import BaseSpider as Spider
import datetime
from items.biding import biding_gov
from utils.toDB import *
from utils.insertTxt import Txt


class hz_gov_Spider(scrapy.Spider):
    name = "dali_zhongbiao.py"
    allowed_domains = ["www.dlggzy.com"]

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'middlewares.useragent_middleware.RandomUserAgent': 400,
            # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
            # 'middlewares.proxy_middleware.ProxyMiddleware': 250,
            # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            # 'middlewares.retry_middleware.RetryWithProxyMiddleware': 300,
            # 'middlewares.timestamp_middleware.TimestampMiddleware': 120
        }
    }

    def start_requests(self):
        urls = [
            "http://www.dlggzy.com/zbtb_list.aspx?etype=1&oid=2&dqid=0",
            "http://www.dlggzy.com/zbtb_list.aspx?etype=2&oid=2&dqid=0"
        ]
        pages = [127, 69, ]
        for i in range(len(urls)):
            yield Request(urls[i], callback=self.parse, meta={'url': urls[i], 'page': pages[i]})

    def parse(self, response):
        url = response.meta['url']
        page = response.meta['page']
        selector = Selector(response)
        start = 2
        __VIEWSTATE = selector.xpath("//input[@id='__VIEWSTATE']/@value").extract()
        __EVENTVALIDATION = selector.xpath("//input[@id='__EVENTVALIDATION']/@value").extract()
        headers = {
            "Cookie": '_gscu_944482443=89729069gfsn3i22; _gscs_944482443=90074081mtbofp22|pv:10; _gscbrs_944482443=1',
            "Referer": url,
            "Host": "www.dlggzy.com"
        }
        while start <= 3:
            yield FormRequest(url=url,
                              formdata={
                                  '__VIEWSTATE': __VIEWSTATE[0],
                                  '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$PageNext',
                                  '__EVENTVALIDATION': __EVENTVALIDATION[0],
                                  '__EVENTARGUMENT': '',
                                  'ContentPlaceHolder1': str(start+1)}, headers=headers,
                              callback=self.middle,meta={'page':str(start)})
            start += 1


    def middle(self, response):
        print "当前是第：" + response.meta['page'] + "页"
        selector = Selector(response)
        urls = selector.xpath("//div[@class='newslist']/ul/li//a/@href").extract()
        for i in urls:
            print i
    #     names=[]
    #     for i in urls:
    #         names.append(selector.xpath("//a[@href='" + i + "']/text()").extract()[0].strip())
    #
    #     for i in range(len(names)):
    #         url = "http://www.jzjjzx.com.cn/" + "".join(urls[i])
    #         str = "".join(names[i]) + "," + url
    #         print str
    #         yield Request(url=url, callback=self.parse2, meta={"info": str})
    #
    # def parse2(self, response):
    #             infos = response.meta["info"]
    #             items = biding_gov()
    #             items["url"] = response.url
    #             items["name"] = "".join(infos).split(",")[0]
    #             items["info"] = ""
    #             items["create_time"] = datetime.datetime.now()
    #             items["update_time"] = datetime.datetime.now()
    #
    #             page_info = "".join(response.body)
    #             items["info"] = "".join(page_info)
    #
    #             Tomogo(
    #                 items["url"],
    #                 items["name"],
    #                 items["info"],
    #                 items["create_time"],
    #                 items["update_time"]
    #             )
    #             print items["url"]
    #             print items["name"]
