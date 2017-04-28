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
# 山东潍坊招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "weifang_zhongbiao.py"
    allowed_domains = ["ggzy.weifang.gov.cn"]

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
            "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg.aspx?categorynums=&categorynums2=&categorynum=004012007&address=&type=&Paging=",
            "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_zfcg.aspx?address=001&type=&categorynum=004002012&Paging=",
        ]
        pages = [19, 106]
        for i in range(len(urls)):
            num = 1
            while num <= pages[i]:
                url = urls[i] + str(num)
                num += 1
                # print url
                yield Request(url=url,callback=self.parse)

    # start_urls = [
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//span[@class='info-name']//a/text()").extract()
        urls = selector.xpath("//span[@class='info-name']//a/@href").extract()
        for i in range(len(names)):
            url = "http://ggzy.weifang.gov.cn" + "".join(urls[i])
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
            "bid_shandong_WeiFang",
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
