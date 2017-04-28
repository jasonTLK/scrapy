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

# 陕西延安招投标网站
# 招标信息


class hz_gov_Spider(scrapy.Spider):
    name = "yanan_zhaobiao.py"
    # allowed_domains = ["ak.gov.cn"]

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
            "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001001/004001001001/?pageing=",
            "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001008/004001008001/?pageing=",
            "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004007/004007001/004007001001/?pageing=",
            "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004007/004007002/004007002001/?pageing="
            "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004007/004007003/004007003001/?pageing="
        ]
        pages=[11, 2, 9, 2, 4]
        for i in range(len(urls)):
            page = 1
            while page<=pages[i]:
                url = urls[i] + str(page)
                page += 1
                # print url
                yield Request(url=url,callback=self.parse)

    # start_urls = [
    #     "http://www.xyzhb.com/zbgg/index_1.jhtml"
    # ]

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//ul/li/div//@href").extract()
        for i in urls:
           print i
        names=[]
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/text()").extract()[0].strip())

        for i in range(len(names)):
            url = "http://www.yaggzyjy.cn"+"".join(urls[i])
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
            "bid_SX_YanAn",
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