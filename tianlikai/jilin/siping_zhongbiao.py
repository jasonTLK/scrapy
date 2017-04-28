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


class hz_gov_Spider(scrapy.Spider):
    name = "siping_zhongbiao.py"

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
        "http://xn--fiq74s75f5maugq9dzzrrq4f5wi.xn--55qw42g.cn/html/tender/tender_2.html"
    ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//div[@class='er-you4']//a/text()").extract()
        urls = selector.xpath("//table[@width='735']//a/@href").extract()

        for i in names:
            print i
    #     for i in range(len(names)):
    #         url = "http://121.28.35.251/" + "".join(urls[i])
    #         str = "".join(names[i]) + "," + url
    #         print str
    #         try:
    #             txt = Txt("c://test/shanxi_shijiazhuang_gov_urls.txt", "a+")
    #             txt.insertToFile(str.encode("utf-8"))
    #         except Exception as e:
    #             print e
    #         finally:
    #             txt.close()
    #         yield Request(url=url, callback=self.parse2, meta={"info": str})
    #
    # def parse2(self, response):
    #     infos = response.meta["info"]
    #     items = biding_gov()
    #     items["url"] = response.url
    #     items["name"] = "".join(infos).split(",")[0]
    #     items["info"] = ""
    #     items["create_time"] = datetime.datetime.now()
    #     items["update_time"] = datetime.datetime.now()
    #
    #     page_info = "".join(response.body)
    #     items["info"] = "".join(page_info)
    #
    #     Tomogo(
    #         items["url"],
    #         items["name"],
    #         items["info"],
    #         items["create_time"],
    #         items["update_time"]
    #     )
    #     print items["url"]
    #     print items["name"]
    #     try:
    #         txt = Txt("c://test/shanxi_shijiazhuang_gov_urls-record.txt", "a+")
    #         txt.insertToFile(infos.encode("utf-8"))
    #     except Exception as e:
    #         print e
    #     finally:
    #         txt.close()
