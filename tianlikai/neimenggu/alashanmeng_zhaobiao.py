# -*- coding: utf-8 -*-
# 内蒙古阿拉善盟招投标网站
# 招标信息
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
    name = "alashanmeng_zhaobiao.py"
    allowed_domains = ["alsggzyjy.cn"]

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
            "http://www.alsggzyjy.cn/website/zyjyzx/html/artList.html?sn=zyjyzx&catCode=cg_zbgg&pageNo=",
            "http://www.alsggzyjy.cn/website/zyjyzx/html/artList.html?sn=zyjyzx&catCode=zbgg&pageNo=",
        ]
        pages = [148, 107]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num)
                num+=1
                yield Request(url=url,callback=self.parse)

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//ul[@class='ul_art_row']//a/@title").extract()
        urls = selector.xpath("//ul[@class='ul_art_row']//a/@href").extract()

        for i in range(len(names)):
            url = "http://www.alsggzyjy.cn" + "".join(urls[i])
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
            "bid_neimeng_AlaShanMeng",
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

