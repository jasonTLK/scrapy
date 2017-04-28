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
# 浙江金华招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "jinhua_zhaobiao.py"
    allowed_domains = ["jhztb.gov.cn"]

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
            "http://www.jhztb.gov.cn/jhztb/gcjyysgs/index",
            "http://www.jhztb.gov.cn/jhztb/jsgcgcjszbgg/index",
            "http://www.jhztb.gov.cn/jhztb/jsgcjhszbgg/index",
            "http://www.jhztb.gov.cn/jhztb/zfcgcggg/index"
        ]
        pages = [3, 24, 2, 73]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                if num==1:
                    url = urls[i]+".htm"
                else:
                    url =urls[i]+"_"+str(num)+".htm"
                num+=1
                # print url
                yield Request(url=url,callback=self.parse)


    # start_urls = [
    #     "http://www.jhztb.gov.cn/jhztb/gcjyzbzy/index_2.htm"
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//div[@class='Right-Border floatL']//a/@title").extract()
        urls = selector.xpath("//div[@class='Right-Border floatL']//a/@href").extract()
        for i in range(len(names)):
            url = "http://www.jhztb.gov.cn" + "".join(urls[i])
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
            "bid_zhejiang_JinHua",
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
