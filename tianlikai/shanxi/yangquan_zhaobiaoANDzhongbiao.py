# -*- coding: utf-8 -*-
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
# 山西阳泉招投标网站
# 中标信息和招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "yangquan_zhaobiaoANDzhongbiao.py"
    allowed_domains = ["prec.sxzwfw.gov.cn"]

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
        while page <= 12:
            url = "http://prec.sxzwfw.gov.cn/Home/SearchDataList?currentPage="+str(page)+"&KeyWord=%E9%98%B3%E6%B3%89%E5%B8%82"
            yield Request(url=url, callback=self.parse)
            page += 1


    # start_urls = [
    #     "http://prec.sxzwfw.gov.cn/Home/SearchDataList?currentPage=1&KeyWord=%E9%98%B3%E6%B3%89%E5%B8%82"
    # ]

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//td[@class='title']//a/@href").extract()
        t = selector.xpath("//tr[@class='td_content']//td/text()").extract()

        types = []
        for i in range(1,len(t),3):
            types.append(t[i])
        names = []
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/text()").extract()[0].strip())

        for i in range(len(names)):
            url = "http://prec.sxzwfw.gov.cn" + "".join(urls[i])
            str = "".join(names[i]) + "," + url
            print str,types[i]
            yield Request(url=url, callback=self.parse2, meta={"info": str, 'type':types[i]})

    def parse2(self, response):
        type = response.meta["type"]
        infos = response.meta["info"]
        items = biding_gov()
        items["url"] = response.url
        items["name"] = "".join(infos).split(",")[0]
        items["info"] = ""
        items["create_time"] = datetime.datetime.now()
        items["update_time"] = datetime.datetime.now()

        page_info = "".join(response.body)
        items["info"] = "".join(page_info)

        if type == u"交易结果":
            print "交易结果"
            db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
            db.get_insert(
                "bid_shanxi_YangQuan",
                {
                    "url": items["url"],
                    "name": items["name"],
                    "info": items["info"],
                    "create_time": items["create_time"],
                    "update_time": items["update_time"]
                }
            )
        else:
            print "交易项目"
            db = MongodbHandle("172.20.3.10 ", 27017, "Biding_announcement")
            db.get_insert(
                "bid_shanxi_YangQuan",
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

