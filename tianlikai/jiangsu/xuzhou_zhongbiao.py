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
# 江苏徐州招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "xuzhou_zhongbiao.py"
    allowed_domains = ["www.ccgp-xuzhou.gov.cn"]

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
        page =1
        while page<=5:
            url = "http://www.ccgp-xuzhou.gov.cn/webinfo/ccgp-web/no2/bid_zb/listindexw.asp?currentpage="+str(page)+"&Bp_type="
            page+=1
            # print url
            yield Request(url=url,callback=self.parse)



    # start_urls = [
    #     "http://www.ccgp-xuzhou.gov.cn/webinfo/ccgp-web/no2/bid_zb/listindexw.asp?currentpage=2&Bp_type="
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//tr[@class='tabdetail1']//a/text()").extract()
        for i in selector.xpath("//tr[@class='tabdetail2']//a/text()").extract():
            names.append(i)
        urls = selector.xpath("//tr[@class='tabdetail1']//a/@href").extract()
        for i in selector.xpath("//tr[@class='tabdetail2']//a/@href").extract():
            urls.append(i)


        for i in range(len(names)):
            url = "http://www.ccgp-xuzhou.gov.cn/webinfo/ccgp-web/no2/bid_zb/" + "".join(urls[i])
            str = "".join(names[i]) + "," + url
            print str
    #         try:
    #             txt = Txt("c://test/shanxi_shijiazhuang_gov_urls.txt", "a+")
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
        items["info"] = "".join(page_info).decode('gbk')

        db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
        db.get_insert(
            "bid_jiangsu_XuZhou",
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
    #         txt = Txt("c://test/shanxi_shijiazhuang_gov_urls-record.txt", "a+")
    #         txt.insertToFile(infos.encode("utf-8"))
    #     except Exception as e:
    #         print e
    #     finally:
    #         txt.close()
