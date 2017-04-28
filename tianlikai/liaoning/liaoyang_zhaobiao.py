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

# 辽宁辽阳招投标网站
# 招标信息
class hz_gov_Spider(scrapy.Spider):
    name = "liaoyang_zhaobiao.py"


    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'middlewares.useragent_middleware.RandomUserAgent': 400,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
            'middlewares.proxy_middleware.ProxyMiddleware': 250,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'middlewares.retry_middleware.RetryWithProxyMiddleware': 300,
            'middlewares.timestamp_middleware.TimestampMiddleware': 120
        }
    }
    def start_requests(self):
        urls = [
            "http://59.45.183.9:81/sitefiles/services/cms/page.aspx?s=1&n=148&p=",
            "http://59.45.183.9:81/sitefiles/services/cms/page.aspx?s=1&n=153&p="
        ]
        pages = [324, 20]
        for i in range(len(urls)):
            page = 1
            while page <= pages[i]:
                url = urls[i] + str(page)
                page += 1
                # print url
                yield Request(url=url, callback=self.parse)


    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//ul[@class='article']//a/@title").extract()
        urls = selector.xpath("//ul[@class='article']//a/@href").extract()

        for i in range(len(names)):
            url = "http://59.45.183.9:81" + "".join(urls[i])
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
            "bid_liaoning_LiaoYang",
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
    # def start_requests(self):
    #     page =0
    #     while page<=14:
    #         url = "http://59.45.183.9:81/sitefiles/services/cms/page.aspx?s=1&n=155&p="+str(page)
    #         page+=1
    #         # print url
    #         yield Request(url=url,callback=self.parse)
    #
    # # start_urls=[
    # #     "http://59.45.183.9:81/sitefiles/services/cms/page.aspx?s=1&n=150&p=2"
    # # ]
    # def parse(self, response):
    #     selector = Selector(response)
    #     names = selector.xpath("//ul[@class='article']//a/@title").extract()
    #     urls = selector.xpath("//ul[@class='article']//a/@href").extract()
    #
    #
    #     for i in range(len(names)):
    #         str ="".join(names[i]) + "," + "http://59.45.183.9:81" + "".join(urls[i])
    #         print str
    #         try:
    #             txt = Txt("c://test/liaoyang_gov_urls.txt","a+")
    #             txt.insertToFile(str.encode("utf-8"))
    #         except Exception as e:
    #             print e
    #         finally:
    #             txt.close()








