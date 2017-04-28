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
from hdfs import Client

# 甘肃白银招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "baiying_zhongbiao.py"

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
            "http://www.bygzjy.cn/Handlers/InfoPageTrade.ashx?pageIndex=",
            "http://www.bygzjy.cn/Handlers/InfoPageTrade.ashx?pageIndex=",
            'http://www.bygzjy.cn/Handlers/InfoPageTrade.ashx?pageIndex='
        ]
        urls2 = [
            "&pageSize=30&siteItem=46&infoType=&query=",
            "&pageSize=30&siteItem=112&infoType=&query=",
            "&pageSize=30&siteItem=120&infoType=&query="
        ]
        pages = [58, 20, 54]
        for i in range(len(urls)):
            num = 1
            while num <= pages[i]:
                url = urls[i] + str(num) + urls2[i]
                num += 1
                # print url
                yield Request(url=url, callback=self.parse)

    # start_urls = [
    #     "http://www.bygzjy.cn/Handlers/InfoPageTrade.ashx?pageIndex=1&pageSize=30&siteItem=46&infoType=&query="
    # ]

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//a[@class='infolist_a']/@href").extract()
        names = []
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/@title").extract()[0].strip())

        for i in range(len(names)):
            url = "".join(urls[i]).replace("../", "http://www.bygzjy.cn/")
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
            "bid_gansu_BaiYin",
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

