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

# 青海海北招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "haibei_zhaobiao.py"
    allowed_domains = ["hbzwzx.gov.cn"]

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
            "http://www.hbzwzx.gov.cn/Front/ggzyjy/006001/006001001/006001001001/006001001001002/?Paging=",
            "http://www.hbzwzx.gov.cn/Front/ggzyjy/006001/006001002/006001002001/006001002001002/?Paging=",
            "http://www.hbzwzx.gov.cn/Front/ggzyjy/006001/006001003/006001003001/006001003001001/?Paging=",
            "http://www.hbzwzx.gov.cn/Front/ggzyjy/006001/006001003/006001003001/006001003001002/?Paging=",
            "http://www.hbzwzx.gov.cn/Front/ggzyjy/006001/006001004/006001004001/006001004001002/?Paging=",
            "http://www.hbzwzx.gov.cn/Front/ggzyjy/006004/006004001/006004001001/?Paging="
        ]
        pages = [5, 1, 3, 1, 2, 7]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num)
                num+=1
                # print url
                yield Request(url=url,callback=self.parse)


    # start_urls = [
    #     "http://www.hbzwzx.gov.cn/Front/ggzyjy/006001/006001001/006001001002/006001001002002/?Paging=1"
    # ]

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//td[@align='left']//a/@href").extract()
        for i in urls:
            print i
        names=[]
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/text()").extract()[0].strip())

        for i in range(len(names)):
            url = "http://www.hbzwzx.gov.cn" + "".join(urls[i])
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
        items["info"] = "".join(page_info).decode('gbk').replace("gb2312","utf-8")


        db = MongodbHandle("172.20.3.10 ", 27017, "Biding_announcement")
        db.get_insert(
            "bid_qinghai_HaiBei",
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