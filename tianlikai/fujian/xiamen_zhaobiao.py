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

# 福建厦门招投标网站
# 招标信息

class hz_gov_Spider(scrapy.Spider):
    name = "xiamen_zhaobiao.py"
    allowed_domains = ["xmzfcg.gov.cn"]

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
        while page<=2882:
            url = "http://www.xmzfcg.gov.cn/stockfile/stockfileAction.do?cmd=stockfile_index&curpage="+str(page)+"&totalPage=&title=&project_name=&serial_number=&public_dateFrom=&public_dateTo=&demander_info=&agency_info=&main_content=&stock_way=0&source_type_str=&pagelines=20&txtgotopage="
            page+=1
            # print url
            yield Request(url=url,callback=self.parse)



    # start_urls = [
    # ]

    def parse(self, response):
        selector = Selector(response)
        names = selector.xpath("//td[@style='BORDER-BOTTOM:1px dashed']//a/text()").extract()
        urls = selector.xpath("//td[@style='BORDER-BOTTOM:1px dashed']//a/@href").extract()


        for i in range(1,len(names),2):
            url = "".join(urls[i]).replace("javascript:ShowView('","http://www.xmzfcg.gov.cn/stockfile/").replace("')","")
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
        items["info"] = "".join(page_info).decode('gbk')


        db = MongodbHandle("172.20.3.10 ", 27017, "Biding_announcement")
        db.get_insert(
            "bid_fujian_XiaMen",
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

