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
# 广东珠海招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "zhuhai_zhongbiao.py"
    allowed_domains = ["ggzy.zhuhai.gov.cn"]

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
            "http://ggzy.zhuhai.gov.cn//zbgs/index_",
            "http://ggzy.zhuhai.gov.cn//zczbgg/index_",
        ]
        urls2 = [
            "http://ggzy.sz.gov.cn/jyxx/gzjsztb/zbjggs/index.htm",
            "http://ggzy.zhuhai.gov.cn//zczbgg/index.htm",
        ]
        pages = [555, 746]
        for i in range(len(urls)):
            num = 1
            while num <= pages[i]:
                if num == 1:
                    url = urls2[i]
                else:
                    url = urls[i] + str(num) + ".htm"
                num += 1
                # print url
                yield Request(url=url, callback=self.parse)


    # start_urls = [
    #     "http://ggzy.zhuhai.gov.cn//zbgs/index.htm"
    # ]

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//ul[@class='news']/li//a/@href").extract()
        for i in urls:
            print i
        names=[]
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/@title").extract()[0].strip())

        for i in range(len(names)):
            url = "".join(urls[i])
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

        db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
        db.get_insert(
            "bid_anhui_AnQing",
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