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
# 江西抚州招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "fuzhou_zhongbiao.py"
    allowed_domains = ["fzztb.gov.cn"]

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
            "http://www.fzztb.gov.cn/jsgc/zbgs/gkzb/index_",
            "http://www.fzztb.gov.cn/zfcg/zbgs/index_",
        ]
        urls2=[
            "http://www.fzztb.gov.cn/jsgc/zbgs/gkzb/index.htm",
            "http://www.fzztb.gov.cn/zfcg/zbgs/index.htm"
        ]
        pages = [16, 16]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                if num==1:
                    url=urls2[i]
                else:
                    url =urls[i]+str(num)+".htm"
                num+=1
                # print url
                yield Request(url=url,callback=self.parse)


    # start_urls = [
    #     "http://www.fzztb.gov.cn/jsgc/zbgs/gkzb/index_1.htm"
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//td[@align='left']//a/@title").extract()
        urls = selector.xpath("//td[@align='left']//a/@href").extract()
        print len(names),len(urls)
        for i in range(len(names)):
            url = "".join(urls[i+4]).replace("./","http://www.fzztb.gov.cn/jsgc/zbgs/gkzb/")
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
            "bid_jiangxi_FuZhou",
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