# -*- coding: utf-8 -*-
# 吉林吉林招投标网站
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
    name = "jilin_zhaobiao.py"
    allowed_domains = ["ggzyjy.jl.gov.cn"]

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
            "http://www.jlsggzyjy.gov.cn/jlsztb/jyxx/003001/003001001/003001001001/?pageing=",
            "http://www.jlsggzyjy.gov.cn/jlsztb/jyxx/003002/003002001/003002001001/?pageing="
        ]
        pages = [56, 127]
        for i in range(len(urls)):
            page = 1
            while page<=pages[i]:
                url = urls[i] + str(page)
                page+=1
                # print url
                yield Request(url=url,callback=self.parse)



    # start_urls = [
    #     "http://ggzyjy.jl.gov.cn/JiLinZtb/Template/Default/MoreInfoJYXX.aspx?CategoryNum=004001"
    # ]

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//ul[@class='ewb-com-items']//a/@href").extract()
        names = []
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/text()").extract()[0].strip())

        for i in range(len(names)):
            url =  "http://www.jlsggzyjy.gov.cn" + "".join(urls[i])
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

        page_info = "".join(response.body).decode('gbk')
        items["info"] = "".join(page_info)

        db = MongodbHandle("172.20.3.10 ", 27017, "Biding_announcement")
        db.get_insert(
            "bid_jilin_JiLin",
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

