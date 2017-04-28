# -*- coding: utf-8 -*-
# 四川德阳招投标网站
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
    name = "deyang_zhongbiao.py"
    allowed_domains = ["dyggzy.com"]

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

    #
    # def start_requests(self):
    #     urls = [
    #         "http://www.qhdggzy.gov.cn/ggzyjyw/bidWinnerList_bidWinnerList.do?pagination.offset=12&p=",
    #         "http://www.qhdggzy.gov.cn/ggzyjyw/article_purchaseGuideList.do?pagination.offset=12&p=",
    #     ]
    #     pages = [75, 74]
    #     for i in range(len(urls)):
    #         num=1
    #         while num<=pages[i]:
    #             url =urls[i]+str(num)
    #             num+=1
    #             print url
    #             # yield Request(url=url,callback=self.parse)


    start_urls = [
        "http://www.dyggzy.com/categoryClass_f28479730cf1488f82b5a5c790c7dc58.html"
    ]

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//div[@class='tab-ul']//a/@href").extract()
        for i in urls:
            print i
        names=[]
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/text()").extract()[0].strip())

        for i in range(len(names)):
            url = "http://www.dyggzy.com/" + "".join(urls[i])
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

        db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
        db.get_insert(
            "bid_sichuan_DeYang",
            {
                "url": items["url"],
                "name": items["name"],
                "info": items["info"],
                "create_time": items["create_time"],
                "update_time": items["update_time"]
            }
        )
