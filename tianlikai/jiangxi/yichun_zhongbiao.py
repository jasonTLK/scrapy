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
# 江西宜春招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "yichun_zhongbiao.py"
    allowed_domains = ["ycztbw.gov.cn"]

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
            "http://www.ycztbw.gov.cn/zbgs/jsgc_5759/index_",
            "http://www.ycztbw.gov.cn/zbgs/gljt_5760/index_",
            "http://www.ycztbw.gov.cn/zbgs/slgc_5761/index_",
            "http://www.ycztbw.gov.cn/zbgs/szyl_5762/index_",
            "http://www.ycztbw.gov.cn/zbgs/zfcg_5763/index_"
        ],
        urls2=[
            "http://www.ycztbw.gov.cn/zbgs/jsgc_5759/index.html",
            "http://www.ycztbw.gov.cn/zbgs/gljt_5760/index.html",
            "http://www.ycztbw.gov.cn/zbgs/slgc_5761/index.html",
            "http://www.ycztbw.gov.cn/zbgs/szyl_5762/index.html",
            "http://www.ycztbw.gov.cn/zbgs/zfcg_5763/index.html"
        ]
        pages = [50, 14, 21, 26, 50]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                if num==1:
                    url = urls2[i]
                else:
                    url =urls[i]+str(num)+ ".html"
                num+=1
                # print url
                yield Request(url=url,callback=self.parse)


    start_urls = [
        "http://www.ycztbw.gov.cn/zbgs/jsgc_5759/index_1.html"
    ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//tr[@class='tdLine']//a/text()").extract()
        urls = selector.xpath("//tr[@class='tdLine']//a/@href").extract()
        for i in range(len(names)):
            url =  "".join(urls[i]).replace("./","http://www.ycztbw.gov.cn/zbgs/jsgc_5759/")
            str = "".join(names[i]).strip() + "," + url
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
            "bid_jiangxi_YiChun",
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