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


class hz_gov_Spider(scrapy.Spider):
    name = "shijiazhuang_zhongbiao.py"
    allowed_domains = ["121.28.35.251"]

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
        page = 1
        while page <= 56:
            url = "http://121.28.35.251/listframe.jsp?id=281&subcatid=&name=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&name2=&type=DIMMENSION_A&pages=" + str(
                page) + "&nouse=1489388983790"
            page += 1
            # print url
            yield Request(url=url, callback=self.parse)

    # start_urls = [
    #     "http://121.28.35.251/listframe.jsp?id=281&subcatid=&name=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&name2=&type=DIMMENSION_A&pages=2&nouse=1489388983790"
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//table[@width='735']//td[@class='tdline']//a/text()").extract()
        urls = selector.xpath("//table[@width='735']//td[@class='tdline']//a/@href").extract()

        for i in range(len(names)):
            url = "http://121.28.35.251/" + "".join(urls[i])
            str = "".join(names[i]) + "," + url

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

        db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
        db.get_insert(
            "bid_heibei_ShiJiaZhuang",
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

