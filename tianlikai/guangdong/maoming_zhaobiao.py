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
# 广东茂名招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "maoming_zhaobiao.py"
    allowed_domains = ["mmgpc.maoming.gov.cn"]

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
            "http://mmgpc.maoming.gov.cn/mmzbtb/jyxx/033001/033001001/033001001001/033001001001001/?Paging=",
            "http://mmgpc.maoming.gov.cn/mmzbtb/jyxx/033001/033001001/033001001001/033001001001002/?Paging="
            "http://mmgpc.maoming.gov.cn/mmzbtb/jyxx/033001/033001001/033001001001/033001001001003/?Paging=",
            "http://mmgpc.maoming.gov.cn/mmzbtb/jyxx/033001/033001001/033001001001/033001001001004/?Paging="
            "http://mmgpc.maoming.gov.cn/mmzbtb/jyxx/033002/033002001/033002001001/033002001001001/?Paging=",
            "http://mmgpc.maoming.gov.cn/mmzbtb/jyxx/033002/033002001/033002001001/033002001001003/?Paging=",
            "http://mmgpc.maoming.gov.cn/mmzbtb/jyxx/033002/033002001/033002001001/033002001001006/?Paging="
        ]
        pages = [23, 7, 7, 3, 72, 9, 2]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num)
                num+=1
                # print url
                yield Request(url=url,callback=self.parse)


    # start_urls = [
    #     "http://mmgpc.maoming.gov.cn/mmzbtb/jyxx/033001/033001001/033001001003/033001001003001/?Paging=1"
    # ]

    def parse(self, response):
        selector = Selector(response)
        u = selector.xpath("//td[@align='left']//a/@href").extract()
        urls =[]
        for i in range(6,len(u)):
            print u[i]
            urls.append(u[i])
        names=[]
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/@title").extract()[0].strip())

        for i in range(len(names)):
            url = "http://mmgpc.maoming.gov.cn" + "".join(urls[i])
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
            "bid_guangdong_MaoMing",
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