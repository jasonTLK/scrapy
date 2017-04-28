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
# 安徽阜阳招投标网站
# 中标信息

class hz_gov_Spider(scrapy.Spider):
    name = "fuyang_zhongbiao.py"
    allowed_domains = ["jyzx.fy.gov.cn"]

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
            "http://jyzx.fy.gov.cn/FuYang/zfcg/011002/011002001/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/zfcg/011002/011002002/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/zfcg/011002/011002003/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/zfcg/011002/011002004/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/zfcg/011002/011002005/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/zfcg/011002/011002006/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/jsgc/012002/012002001/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/jsgc/012002/012002002/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/jsgc/012002/012002003/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/jsgc/012002/012002004/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/jsgc/012002/012002005/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/jsgc/012002/012002006/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/jtys/013002/013002001/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/jtys/013002/013002004/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/jtys/013002/013002005/?pageing="
        ]
        pages = [10, 6, 2, 6, 5, 7, 9, 6, 4, 8, 2, 3, 2, 3, 2]
        for i in range(len(urls)):
            num=1
            while num<=pages[i]:
                url =urls[i]+str(num)
                num+=1
                # print url
                yield Request(url=url,callback=self.parse)


    # start_urls = [
    #     "http://jyzx.fy.gov.cn/FuYang/zfcg/011002/011002001/?pageing=1"
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//div[@name='zwgk']/ul//a/@title").extract()
        urls = selector.xpath("//div[@name='zwgk']/ul//a/@href").extract()
        for i in range(len(names)):
            url = "http://jyzx.fy.gov.cn" + "".join(urls[i])
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
        items["info"] = "".join(page_info).decode('gbk')

        db = MongodbHandle("172.20.3.10 ", 27017, "spiderBiding")
        db.get_insert(
            "bid_anhui_FuYang",
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
