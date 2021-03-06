# -*- coding: utf-8 -*-
#  内蒙古兴安盟招投标网站
#  中标信息
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
    name = "xinganmeng_zhongbiao.py"
    allowed_domains = ["ggzy.xam.gov.cn"]

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
            "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001001/004001001004/?pageing=",
            "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001002/004001002004/?pageing=",
            "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001003/004001003004/?pageing=",
            "http://ggzy.xam.gov.cn/xamggzy/jyxx/004002/004002002/?pageing="
        ]
        pages = [12, 4, 2, 13]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num)
                num+=1
                yield Request(url=url,callback=self.parse)


    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//li[@class='list-body-item']//a//span[@class='list-link-left l']/text()").extract()
        urls = selector.xpath("//li[@class='list-body-item']//a//@href").extract()

        for i in range(len(names)):
            url = "http://ggzy.xam.gov.cn" + "".join(urls[i])
            str = "".join(names[i]).strip() + "," + url
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
        items["info"] = "".join(page_info).decode("gbk")

        db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
        db.get_insert(
            "bid_neimeng_xingAnMeng",
            {
                "url": items["url"],
                "name": items["name"],
                "info": items["info"],
                "create_time": items["create_time"],
                "update_time": items["update_time"]
            }
        )
