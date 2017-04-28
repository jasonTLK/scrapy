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

# 福建莆田招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "putian_zhaobiao.py"
    allowed_domains = ["ptfwzx.gov.cn"]

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
            "http://www.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002001/004003002001001/?Paging=",
            "http://www.ptfwzx.gov.cn/fwzx/wjzyzx/004002/004002005/004002005002/?Paging=",
            "http://www.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002002/004003002002001/?Paging=",
            "http://www.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002002/004003002002002/?Paging=",
            "http://www.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002002/004003002002004/?Paging=",
            "http://www.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002004/004003002004001/?Paging=",
            "http://www.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002004/004003002004007/?Paging=",
            "http://www.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002005/004003002005001/?Paging=",
            "http://www.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002005/004003002005002/?Paging=",
            "http://www.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002005/004003002005003/?Paging=",
            "http://www.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002005/004003002005004/?Paging=",
            "http://www.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002005/004003002005007/?Paging="
        ]
        pages = [1, 171, 31, 13, 7, 6, 2, 22, 4, 8, 6, 123]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num)
                num+=1
                # print url
                yield Request(url=url,callback=self.parse)


    # start_urls = [
    #     "http://www.ptfwzx.gov.cn/fwzx/wjzyzx/004002/004002010/004002010002/?Paging=1"
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//td[@align='left']//a/@title").extract()
        urls = selector.xpath("//td[@align='left']//a/@href").extract()
        print len(names),len(urls)
        for i in range(len(names)):
            url = "http://www.ptfwzx.gov.cn" + "".join(urls[i+4])
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
            "bid_fujian_PuTian",
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