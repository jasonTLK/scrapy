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

# 湖南永州招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "yongzhou_zhaobiao.py"
    allowed_domains = ["ggzy.yzcity.gov.cn"]

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
            "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001001/004001001001/?Paging=",
            "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001001/004001001002/?Paging=",
            "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001001/004001001003/?Paging=",
            "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004002/004002001/004002001001/?Paging=",
            "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004002/004002001/004002001002/?Paging=",
            "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004002/004002001/004002001003/?Paging="
        ]
        pages = [38, 5, 8, 17, 45, 23]
        for i in range(len(urls)):
            num=1
            while num <= pages[i]:
                url = urls[i]+str(num)
                num += 1
                # print url

            yield Request(url=url, callback=self.parse)

    # start_urls = [
    #     "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001004/004001004001/?Paging=1"
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//td[@width='410']//a/@title").extract()
        urls = selector.xpath("//td[@width='410']//a/@href").extract()


        for i in range(len(names)):
            url = "http://ggzy.yzcity.gov.cn" + "".join(urls[i])
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
        items["info"] = "".join(page_info).decode('gbk')


        db = MongodbHandle("172.20.3.10 ", 27017, "Biding_announcement")
        db.get_insert(
            "bid_hunan_YongHua",
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