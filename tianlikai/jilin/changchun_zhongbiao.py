# -*- coding: utf-8 -*-
# 吉林长春招投标网站
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
    name = "changchun_zhongbiao.py"
    allowed_domains = ["ccgp.com.cn"]

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
        while page<=295:
            url =  "http://www.ccgp.com.cn/ccgp/list/resultlistF.jsp?toPage="+str(page)+"&type=&bulletin_name=&purchase_id="
            page+=1
            # print url
            yield Request(url=url,callback=self.parse)



    # start_urls = [
    #     "http://www.ccgp.com.cn/ccgp/list/resultlistF.jsp?toPage=2&type=&bulletin_name=&purchase_id="
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//tr[@height='22']//a/text()").extract()
        urls = selector.xpath("//tr[@height='22']//a/@href").extract()

        for i in range(len(names)):
            url = "".join(urls[i]).replace("./" , "http://www.ccgp.com.cn/ccgp/list/")
            str = "".join(names[i]) + "," + url
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
            "bid_jilin_ChangChun",
            {
                "url": items["url"],
                "name": items["name"],
                "info": items["info"],
                "create_time": items["create_time"],
                "update_time": items["update_time"]
            }
        )