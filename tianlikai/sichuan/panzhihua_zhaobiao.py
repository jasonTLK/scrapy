# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.selector import Selector
# 四川攀枝花招投标网站
# 招标信息
try:
    from scrapy.spiders import Spider
except:
    from scrapy.spiders import BaseSpider as Spider
import datetime
from items.biding import biding_gov
from utils.toDB import *


class hz_gov_Spider(scrapy.Spider):
    name = "panzhihua_zhaobiao.py"
    allowed_domains = ["pzhjs.com"]

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
            "http://www.pzhjs.com/JyWeb/XXGK/JYXTXXListGetXX?PageIndex=",
            "http://www.pzhjs.com/JyWeb/XXGK/JYXTXXListGetXX?PageIndex="
        ]
        urls2 = [
            "&PageSize=15&SubType=1&SubType2=1010&X-Requested-With=XMLHttpRequest",
            "&PageSize=15&SubType=2&SubType2=2010&X-Requested-With=XMLHttpRequest"
        ]
        pages = [40,73]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num)+urls2[i]

                num+=1
                # print url
                yield Request(url=url,callback=self.parse)


    # start_urls = [
    #     "http://www.pzhjs.com/JyWeb/XXGK/JYXTXXListGetXX?PageIndex=1&PageSize=15&SubType=1&SubType2=1030&X-Requested-With=XMLHttpRequest"
    # ]

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//tr[@class='ListTableOddRow']//a/@href").extract()
        for i in urls:
            print i
        names=[]
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/span/@title").extract()[0].strip())

        for i in range(len(names)):
            url = "http://www.pzhjs.com" + "".join(urls[i])
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
            "bid_sichuan_PanZhiHua",
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