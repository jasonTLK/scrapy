# -*- coding: utf-8 -*-
# 云南德宏招投标网站
# 招标、中标信息
import scrapy
from scrapy import Request
from scrapy.selector import Selector

try:
    from scrapy.spiders import Spider
except:
    from scrapy.spiders import BaseSpider as Spider
import datetime
from items.biding import biding_gov
from utils.toDB import *


class hz_gov_Spider(scrapy.Spider):
    name = "dehong_zhaobiaoANDzhongbiao.py"
    # allowed_domains = ["ak.gov.cn"]

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
        page =1
        while page <= 1595:
            url = "http://www.dhggzy.yn.gov.cn/web/infolist.aspx?p=6,{17,21,25,29,34}&page="+str(page)
            yield Request(url=url, callback=self.parse)
            print url
            page += 1

    # start_urls = [
    #     "http://www.ak.gov.cn/gov/publicinfo/category-5_1.html"
    # ]

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//div[@class='right_text']//a/@href").extract()
        for i in urls:
            print "".join(i)
        names = []
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/text()").extract()[0].strip())

        for i in range(len(names)):
            url = "http://www.dhggzy.yn.gov.cn"+"".join(urls[i])
            str = "".join(names[i]) + "," + url
            print str
            yield Request(url=url, callback=self.parse2, meta={"info": str})

    def parse2(self, response):
        infos = response.meta["info"]
        items = biding_gov()
        items["url"] = response.url
        items["name"] = "".join(infos).split(",")[0]
        items["info"] = ""
        items["create_time"] = datetime.datetime.now()
        items["update_time"] = datetime.datetime.now()

        page_info = "".join(response.body)
        items["info"] = "".join(page_info)

        if "".join(items["name"]).find(u"中标公示") >=0 or "".join(items["name"]).find(u"结果公告") >=0 or "".join(items["name"]).find(u"成交公示") >=0:
            print "交易结果"
            # 招标
            db = MongodbHandle("172.20.3.10 ", 27017,"Biding_announcement")
            db.get_insert(
                "bid_yunnan_DeHong",
                {
                    "url":  items["url"],
                    "name": items["name"],
                    "info": items["info"],
                    "create_time": items["create_time"],
                    "update_time": items["update_time"]
                }
            )
        else:
            print "交易项目"
            # 中标
            db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
            db.get_insert(
                "bid_yunnan_DeHong",
                {
                    "url": items["url"],
                    "name": items["name"],
                    "info": items["info"],
                    "create_time": items["create_time"],
                    "update_time": items["update_time"]
                }
            )
        print items["url"]
        print items["name"]

