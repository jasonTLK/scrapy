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
# 新疆博州招投标网站
# 招标信息


class hz_gov_Spider(scrapy.Spider):
    name = "bozhou_zhaobiao.py"
    allowed_domains = ["xzfw.xjboz.gov.cn"]

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
            "http://xzfw.xjboz.gov.cn/btc_web/articleWeb!list.action?startIndex=",
            "http://xzfw.xjboz.gov.cn/btc_web/articleWeb!list.action?startIndex=",
            "http://xzfw.xjboz.gov.cn/btc_web/articleWeb!list.action?startIndex=",
            "http://xzfw.xjboz.gov.cn/btc_web/articleWeb!list.action?startIndex="
        ]

        urls2=[
            "&resourceCode=jszbgg&type=js",
            "&resourceCode=cgzbgg&type=cg",
            "&resourceCode=slzbgg&type=sl",
            "&resourceCode=jtzbgg&type=jt"
        ]
        pages = [1350, 2070, 300, 180]
        for i in range(len(urls)):
            num=0
            while num<=pages[i]:
                url =urls[i]+str(num)
                num+=15
                # print url
                yield Request(url=url,callback=self.parse)


    # start_urls = [
    #     "http://xzfw.xjboz.gov.cn/btc_web/articleWeb!list.action?startIndex=0&resourceCode=jszbgs&type=js"
    # ]

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//td[@class='in_newslist_left']//a/@href").extract()
        for i in urls:
            print i
        names=[]
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/text()").extract()[0].strip())

        for i in range(len(names)):
            url = "http://xzfw.xjboz.gov.cn/btc_web/" + "".join(urls[i])
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
            "bid_xinjiang_BoErTaLa",
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