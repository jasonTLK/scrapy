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
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "fuyang_zhaobiao.py"
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
            "http://jyzx.fy.gov.cn/FuYang/zfcg/011001/011001001/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/jsgc/012001/012001001/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/jtys/013001/013001001/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/slgc/014001/014001001/?pageing=",
            "http://jyzx.fy.gov.cn/FuYang/shfw/017001/017001001/?pageing=",

        ]
        pages = [14, 9, 3, 1, 3]
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

        db = MongodbHandle("172.20.3.10 ", 27017, "Biding_announcement")
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
