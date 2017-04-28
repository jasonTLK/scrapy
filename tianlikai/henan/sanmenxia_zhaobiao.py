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
# 河南三门峡招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "sanmenxia_zhaobiao.py"
    allowed_domains = ["smxgzjy.org"]

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
            "http://www.smxgzjy.org/zbgg/index_",
            "http://www.smxgzjy.org/cggg/index_",
        ]
        urls2 = [
            "http://www.smxgzjy.org/zbgg/index.jhtml",
            "http://www.smxgzjy.org/cggg/index.jhtml"
        ]
        pages = [39, 41]
        for i in range(len(urls)):
            num = 1
            while num <= pages[i]:
                if num == 1:
                    url = urls2[i]
                else:
                    url = urls[i] + str(num) + ".jhtml"
                num += 1
                # print url
                yield Request(url=url, callback=self.parse)

    # start_urls = [
    #     "http://www.smxgzjy.org/zbgs/index_"
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//div[@class='List1']//a/@title").extract()
        urls = selector.xpath("//div[@class='List1']//a/@href").extract()
        for i in range(len(names)):
            url = "http://www.smxgzjy.org" + "".join(urls[i])
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


        db = MongodbHandle("172.20.3.10 ", 27017, "Biding_announcement")
        db.get_insert(
            "bid_henan_SanMenXia",
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