# -*- coding: utf-8 -*-
# 吉林白城招投标网站
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
from utils.insertTxt import Txt


class hz_gov_Spider(scrapy.Spider):
    name = "baicheng_zhongbiao.py"
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

    # def start_requests(self):
    #     page =1
    #     while page<=111:
    #         url = "http://ylgcjyzx.com/news_more3.asp?page="+str(page)+"&word=&lm=&lm2=83&lmname=&open=&n=&hot=&tj="
    #         page+=1
    #         # print url
    #         yield Request(url=url,callback=self.parse)



    start_urls = [
        "http://ggzyjy.jl.gov.cn/JiLinZtb/Template/Default/MoreInfoJYXX.aspx?CategoryNum=004001"
    ]

    def parse(self, response):
        selector = Selector(response)
        u = selector.xpath("//td[@valign='top']//a/@href").extract()
        urls = []
        for i in range(11,22):
            urls.append(u[i])
        names = []
        for i in urls:
            names.append(selector.xpath("//a[@href='" + i + "']/@title").extract()[0].strip())

        for i in range(len(names)):
            url = "".join(urls[i]).replace("../../","http://ggzyjy.jl.gov.cn/JiLinZtb/infodetail/")
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
            "bid_jilin_BaiCheng",
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

