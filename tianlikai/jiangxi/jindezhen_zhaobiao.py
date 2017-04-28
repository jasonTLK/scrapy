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
# 江西景德镇招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "jindezhen_zhaobiao.py"
    allowed_domains = ["jdzggzyjy.com"]

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
            "http://www.jdzggzyjy.com/xwlist.asp?page=",
            "http://www.jdzggzyjy.com/xwlist.asp?page=",
            "http://www.jdzggzyjy.com/xwlist.asp?page=",
            "http://www.jdzggzyjy.com/xwlist.asp?page="
        ]
        pages = [143, 12, 15, 179]
        ids=[
            "&id=17",
            "&id=27"
            "&id=19",
            "&id=20"
        ]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num) + ids[i]
                num+=1
                # print url
                yield Request(url=url,callback=self.parse)


    # start_urls = [
    #     "http://www.jdzggzyjy.com/xwlist.asp?page=2&id=57"
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//table[@align='center']//a/text()").extract()
        urls = selector.xpath("//table[@align='center']//a/@href").extract()
        for i in range(4,len(names)):
            url = "http://www.jdzggzyjy.com/" + "".join(urls[i+4])
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
            "bid_jiangxi_JingDeZhen",
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