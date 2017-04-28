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
# 河北邢台招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "xingtai_zhaobiao.py"
    allowed_domains = ["www.xingtai.gov.cn"]

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
        page = 1
        while page <= 50:
            url = "http://www.xingtai.gov.cn/zwgk/zwzt/zfcg/zbgg/index_" + str(page) + ".html"
            page += 1
            # print url
            yield Request(url=url, callback=self.parse)

    # start_urls = [
    #     "http://www.xingtai.gov.cn/zwgk/zwzt/zfcg/zbgs/index_2.html"
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//table[@class='bot10']//a/@title").extract()
        urls = selector.xpath("//table[@class='bot10']//a/@href").extract()

        for i in range(len(names)):
            url = "".join(urls[i]).replace("./", "http://www.xingtai.gov.cn/zwgk/zwzt/zfcg/zbgs/")
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
        items["info"] = "".join(page_info).decode("gbk")
        db = MongodbHandle("172.20.3.10 ", 27017, "Biding_announcement")
        db.get_insert(
            "bid_heibei_XingTai",
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

