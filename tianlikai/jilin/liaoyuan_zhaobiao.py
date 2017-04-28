# -*- coding: utf-8 -*-
# 吉林辽源招投标网站
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
    name = "liaoyuan_zhaobiao.py"
    allowed_domains = ["liaoyuan.gov.cn"]

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
        while page<=108:
            if page==1:
                url="http://www.liaoyuan.gov.cn/html/zwgk/zfcg/zbgg/index.html"
            else:
                url = "http://www.liaoyuan.gov.cn/html/zwgk/zfcg/zbgg/"+str(page)+".html"
            page+=1
            # print url
            yield Request(url=url,callback=self.parse)



    # start_urls = [
    #     "http://www.liaoyuan.gov.cn/html/zwgk/zfcg/zbgg1/3.html"
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//div[@class='tongzhi']/ul/li//a/text()").extract()
        urls = selector.xpath("//div[@class='tongzhi']/ul/li//a/@href").extract()

        for i in range(len(names)):
            url = "".join(urls[i])
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

        db = MongodbHandle("172.20.3.10 ", 27017, "Biding_announcement")
        db.get_insert(
            "bid_jilin_LiaoYuan",
            {
                "url": items["url"],
                "name": items["name"],
                "info": items["info"],
                "create_time": items["create_time"],
                "update_time": items["update_time"]
            }
        )
