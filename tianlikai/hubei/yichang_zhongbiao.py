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

# 湖北宜昌招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "yichang_zhongbiao.py"
    allowed_domains = ["ycztb.com"]

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
            "http://www.ycztb.com/TPFront/jyxx/003001/003001004/003001004001/?pageing=",
            "http://www.ycztb.com/TPFront/jyxx/003001/003001004/003001004002/?pageing=",
            "http://www.ycztb.com/TPFront/jyxx/003001/003001004/003001004003/?pageing=",
            "http://www.ycztb.com/TPFront/jyxx/003002/003002003/003002003001/?pageing=",
            "http://www.ycztb.com/TPFront/jyxx/003002/003002003/003002003002/?pageing="
        ]
        pages = [6, 2, 2, 5, 3]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num)
                num+=1
                # print url
                yield Request(url=url,callback=self.parse)


    # start_urls = [
    #     "http://www.ycztb.com/TPFront/jyxx/003001/003001004/003001004001/?pageing=1"
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//a[@class='ellipsis']/@title").extract()
        urls = selector.xpath("//a[@class='ellipsis']/@href").extract()

        for i in range(len(names)):
            url = "http://www.ycztb.com" + "".join(urls[i])
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

        db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
        db.get_insert(
            "bid_hubei_YiChang",
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