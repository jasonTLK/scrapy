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

# 辽宁铁岭招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "tieling_zhaobiao.py"
    allowed_domains = ["tlggzyjy.com"]

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
            "http://tlggzyjy.com/Project/Index/",
           "http://tlggzyjy.com/Project/Index/"
        ]
        url2=[
          "?ProjectState=1&CountyId=1&TradeTypeId=1",
            "?ProjectState=1&CountyId=1&TradeTypeId=2"
        ]
        pages = [19, 3]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                if num==1:
                    url="http://tlggzyjy.com/Project"+url2[i]
                else:
                    url =urls[i]+str(num)+url2[i]
                num+=1
                # print url
                yield Request(url=url,callback=self.parse)


    # start_urls = [
    #     "http://tlggzyjy.com/Project/Index/2?ProjectState=3&CountyId=1&TradeTypeId=1"
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//div[@class='page_r_list']//a/text()").extract()
        urls = selector.xpath("//div[@class='page_r_list']//a/@href").extract()
        for i in range(len(names)):
            url = "http://tlggzyjy.com" + "".join(urls[i])
            str = "".join(names[i]) + "," + url
            print str
    #         try:
    #             txt = Txt("c://test/shanxi_qinhuangdao_gov_urls.txt", "a+")
    #             txt.insertToFile(str.encode("utf-8"))
    #         except Exception as e:
    #             print e
    #         finally:
    #             txt.close()
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
            "bid_liaoning_TieLing",
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
    #     try:
    #         txt = Txt("c://test/shanxi_qinhuangdao_gov_urls-record.txt", "a+")
    #         txt.insertToFile(infos.encode("utf-8"))
    #     except Exception as e:
    #         print e
    #     finally:
    #         txt.close()
