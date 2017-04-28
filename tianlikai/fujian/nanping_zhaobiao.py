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

# 福建南平招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "nanping_zhaobiao.py"

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
        while page<=96:
            url = "http://www.npzbtb.gov.cn:8081/bidding/project/listNotices.shtml?type=bidopenings&page="+str(page)
            page+=1
            # print url
            yield Request(url=url, callback=self.parse)



    # start_urls = [
    #     "http://www.npzbtb.gov.cn:8081/bidding/project/listNotices.shtml?type=biddingPitchons&page=2"
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//td[@class='dotline']//a/text()").extract()
        urls = selector.xpath("//td[@class='dotline']//a/@href").extract()

        for i in range(4,len(names),6):
            url = "http://www.npzbtb.gov.cn:8081" + "".join(urls[i])
            str = "".join(names[i]) + "," + url
            print url
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


        db = MongodbHandle("172.20.3.10 ", 27017, "Biding_announcement")
        db.get_insert(
            "bid_fujian_NanPing",
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

