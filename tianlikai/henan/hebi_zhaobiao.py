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
# 河南鹤壁招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "hebi_zhaobiao.py"
    allowed_domains = ["ggzy.hebi.gov.cn"]

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
           "http://ggzy.hebi.gov.cn/TPFront/gcjs/013001/?Paging=",
            'http://ggzy.hebi.gov.cn/TPFront/zfcg/014002/?Paging='
        ]
        pages = [56, 49, ]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num)
                num+=1
                # print url
                yield Request(url=url,callback=self.parse)

    #
    # start_urls = [
    #     "http://ggzy.hebi.gov.cn/TPFront/gcjs/013004/?Paging=1"
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//td[@align='left']//a/@title").extract()
        urls = selector.xpath("//td[@align='left']//a/@href").extract()
        print len(names),len(urls)
        for i in range(len(names)):
            url = "http://ggzy.hebi.gov.cn" + "".join(urls[i+11])
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
        items["info"] = "".join(page_info).replace("gb2312","utf-8")

        db = MongodbHandle("172.20.3.10 ", 27017, "Biding_announcement")
        db.get_insert(
            "bid_henan_HeBi",
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