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
import json
# 江苏无锡招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "wuxi_zhongbiao.py"
    allowed_domains = ["http://www.szzyjy.com.cn"]


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
        while page<=54:
            url = "http://www.wuxi.gov.cn/intertidwebapp/govChanInfo/getDocuments?pageIndex="+str(page)+"&pageSize=20&siteId=2&ChannelType=1&KeyWord=&KeyWordType=&chanId=211"
            page+=1
            yield Request(url=url,callback=self.parse)

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//table//a/font/text()").extract()
        urls = selector.xpath("//table//a/@href").extract()
        data= json.loads("".join(response.body))
        items = data["list"]
        for i in items:
            str ="".join(i["title"]) + "," + "http://www.wuxi.gov.cn" + "".join(i["url"])
            url = "".join(i["url"])
            yield Request(url=url, callback=self.parse2, meta={"info": items[i]})

    def parse2(self, response):
        infos = response.meta["info"]
        items = biding_gov()
        items["url"] = response.url
        items["name"] = "".join(infos).split(",")[0]
        items["info"] = ""
        items["create_time"] = datetime.datetime.now()
        items["update_time"] = datetime.datetime.now()

        page_info = "".join(response.body)
        items["info"] = page_info

        db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
        db.get_insert(
            "bid_jiangsu_WuXi",
            {
                "url": items["url"],
                "name": items["name"],
                "info": items["info"],
                "create_time": items["create_time"],
                "update_time": items["update_time"]
            }
        )
        print infos






