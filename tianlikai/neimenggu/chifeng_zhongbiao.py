# -*- coding: utf-8 -*-
# 内蒙古赤峰招投标网站
# 中标信息
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
    name = "chifeng_zhongbiao.py"
    allowed_domains = ["http://www.gzsggzyjyzx.cn"]


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
        while page<=19:
            url =  "http://www.cfggzy.cn/EpointWeb_CF/jyxx_cf/003002/003002002/003002002003/?Paging="+str(page)
            page+=1
            yield Request(url=url,callback=self.parse)

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//table//a/@title").extract()
        urls = selector.xpath("//table//a/@href").extract()

        for i in range(len(names)):
            str ="".join(names[i]) + "," + "http://www.cfggzy.cn" + "".join(urls[i])

            url = "http://www.cfggzy.cn" + "".join(urls[i])
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
            "bid_neimenggu_ChiFeng",
            {
                "url": items["url"],
                "name": items["name"],
                "info": items["info"],
                "create_time": items["create_time"],
                "update_time": items["update_time"]
            }
        )
        print infos







