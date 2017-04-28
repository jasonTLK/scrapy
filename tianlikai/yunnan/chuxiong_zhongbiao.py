# -*- coding: utf-8 -*-
# 云南楚雄招投标网站
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
    name = "chuxiong_zhongbiao.py"
    allowed_domains = ["cxzwfw.gov.cn"]

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
            "http://www.cxzwfw.gov.cn/ggzyjy/zfcg/zfcg_zbgs/",
            "http://www.cxzwfw.gov.cn/ggzyjy/gcjs/gcjs_zbgg1/",
        ]
        urls2=[
            "http://www.cxzwfw.gov.cn/ggzyjy/zfcg/zfcg_zbgs.htm",
            "http://www.cxzwfw.gov.cn/ggzyjy/gcjs/gcjs_zbgg1.htm"
        ]
        pages = [19, 18]
        for i in range(len(urls)):
            num=0
            while num<=pages[i]:
                if num==0:
                    url = urls2[i]
                else:
                    url =urls[i]+str(num)+".htm"
                num+=1
                # print url
                yield Request(url=url,callback=self.parse,meta={"u":url})

    #
    # start_urls = [
    #     "http://www.cxzwfw.gov.cn/ggzyjy/zfcg/zfcg_zbgs.htm"
    # ]

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//a[@class='c1043']/@href").extract()
        headers = {
            "Cookie": "JSESSIONID=168CD81301B9CC2EEE9657ADE2E57BD5; _gscu_1845518736=89728121qofcid18; _gscs_1845518736=9016463306g3j018|pv:7; _gscbrs_1845518736=1",
            "Host":"www.cxzwfw.gov.cn",
            "Referer": response.meta['u']
        }
        names=[]
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/text()").extract()[0].strip())

        for i in range(len(names)):
            url =  "".join(urls[i]).replace("../../../","http://www.cxzwfw.gov.cn/")
            str = "".join(names[i]) + "," + url
            print str
            yield Request(url=url, callback=self.parse2, meta={"info": str},headers=headers)
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
            "bid_yunnan_ChuXiong",
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