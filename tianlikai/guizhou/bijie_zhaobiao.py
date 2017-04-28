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

# 贵州毕节招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "bijie_zhaobiao.py"
    allowed_domains = ["bjggzy.cn"]

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
           "http://www.bjggzy.cn/gjsgc/index_",
            "http://www.bjggzy.cn/gzfcg/index_"
        ]
        urls2=[
            "http://www.bjggzy.cn/gjsgc/index.jhtml",
            "http://www.bjggzy.cn/gzfcg/index.jhtml"
        ]
        pages = [209, 125]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num)+".jhtml"
                num+=1
                # print url
                yield Request(url=url,callback=self.parse,cookies={"Cookie":"_gscu_1160338151=89719304hxcd5w18; _gscs_1160338151=897193042o41lz18|pv:18; _gscbrs_1160338151=1; clientlanguage=zh_CN"})


    # start_urls = [
    #
    # ]

    def parse(self, response):
        selector = Selector(response)
        urls = selector.xpath("//div[@class='TabbedPanelsContent'][4]//a/@href").extract()
        names=[]
        for i in range(12):
            names.append(selector.xpath("//a[@href='" + urls[i] + "']/@title").extract()[0].strip())

        for i in range(len(names)):
            url = "http://www.bjggzy.cn" + "".join(urls[i])
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
            "bid_guizhou_BiJie",
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